import os, time, threading, requests

class AgentOS:
    def __init__(self, url=None, key=None):
        self.url = (url or os.getenv('AGENTOS_URL', 'http://localhost:8080')).rstrip('/')
        self.key = key or os.getenv('AGENTOS_KEY', '')
        self.headers = {'Authorization': f'Bearer {self.key}', 'Content-Type': 'application/json'}
        self.agent_id = None
        self.running = False
        self.insecure_tls = os.getenv('AGENTOS_INSECURE_TLS') == '1'

    def _post(self, path, body, timeout=10):
        try:
            return requests.post(f'{self.url}{path}', headers=self.headers, json=body, timeout=timeout, verify=not self.insecure_tls)
        except Exception as e:
            print(f'[agentos-sdk] {path} error: {e}')
            return None

    def _register(self, manifest):
        for _ in range(40):
            r = self._post('/api/v1/agents/register', manifest, 5)
            if r is not None and r.status_code < 300:
                print(f'[agentos-sdk] Registered as {self.agent_id}')
                return True
            time.sleep(3)
        return False

    def _heartbeat(self):
        while self.running:
            self._post(f'/api/v1/agents/{self.agent_id}/heartbeat', {}, 5)
            time.sleep(20)

    @staticmethod
    def _split(result):
        # standard handler returns {"output":..,"usage":..}; legacy returns raw output
        if isinstance(result, dict) and 'output' in result:
            return result.get('output'), (result.get('usage') or {})
        return result, {}

    def _run_job(self, job, handler):
        inp = job.get('input', {}) or {}
        action = job.get('action')
        try:
            output, usage = self._split(handler(action, inp))
            payload = {'status': 'success', 'output': output, 'usage': usage}
        except Exception as e:
            payload = {'status': 'failed', 'output': {'error': str(e)}, 'usage': {}}
        self._post(f"/api/v1/jobs/{job['id']}/callback", payload, 60)

    def _poll(self, handler):
        while self.running:
            try:
                r = requests.get(f'{self.url}/api/v1/agents/{self.agent_id}/jobs', headers=self.headers, timeout=10, verify=not self.insecure_tls)
                if r.status_code == 200:
                    for job in (r.json() or []):
                        threading.Thread(target=self._run_job, args=(job, handler), daemon=True).start()
            except Exception as e:
                print('[agentos-sdk] poll error:', e); time.sleep(5)
            time.sleep(3)

    def run(self, manifest, handler):
        if not self.key:
            print('[agentos-sdk] AGENTOS_KEY missing'); return
        self.agent_id = manifest.get('agent_id')
        if not self.agent_id:
            print('[agentos-sdk] manifest needs agent_id'); return
        self.running = True
        if not self._register(manifest):
            print('[agentos-sdk] register failed'); return
        threading.Thread(target=self._heartbeat, daemon=True).start()
        threading.Thread(target=self._poll, args=(handler,), daemon=True).start()
        try:
            while True: time.sleep(60)
        except KeyboardInterrupt:
            self.running = False
