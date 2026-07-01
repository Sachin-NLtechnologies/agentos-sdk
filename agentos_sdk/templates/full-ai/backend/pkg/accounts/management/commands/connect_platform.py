from django.core.management.base import BaseCommand
import os
import requests
from agentos_sdk import AgentOS

class Command(BaseCommand):
    help = 'Connects the AI agent to the AgentOS platform'

    def handle(self, *args, **options):
        self.stdout.write('Starting AgentOS AI connector...')
        
        # ── AgentOS action contract ───────────────────────────────────────────────
        # Everything in manifest['actions'] becomes a "Run" button on the AgentOS platform.
        # When someone clicks Run, the platform calls handler(action, payload) below with
        # {action, input}. Return {"output": {...}, "usage": {...}} and it shows on the platform.
        # Add an action: (1) add {'label','action'} to manifest['actions'];
        #                (2) add an `if action == 'YOUR_ACTION':` branch in handler.
        # You never edit platform code — this manifest is the whole contract.
        # ──────────────────────────────────────────────────────────────────────────
        manifest = {
            'agent_id': os.getenv('AGENTOS_AGENT_ID', '__AGENT_ID__'),
            'version': '1.0.0',
            'team': 'core',
            'capabilities': ['example'],
            'actions': [
                {'label': 'Query Local AI Model', 'action': 'EXAMPLE'},
            ],
            'ui_url': os.getenv('AGENTOS_UI_URL', f"http://localhost:{os.getenv('AGENT_PORT', '3001')}"),
        }

        def handler(action, payload):
            action = (action or '').upper()
            if action == 'EXAMPLE':
                text = payload.get('text', 'Hello, how are you?')
                ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
                vlm_model = os.getenv('VLM_MODEL', 'qwen2.5vl:3b')
                try:
                    r = requests.post(
                        f"{ollama_url}/api/chat",
                        json={
                            "model": vlm_model,
                            "messages": [{"role": "user", "content": text}],
                            "stream": False,
                            "keep_alive": "1h"
                        },
                        timeout=(10, 600)
                    )
                    if r.status_code == 200:
                        ans = r.json().get('message', {}).get('content', '')
                        return {
                            'output': {'response': ans},
                            'usage': {'tokens_in': len(text.split()), 'tokens_out': len(ans.split()), 'cost': 0.0}
                        }
                    else:
                        raise Exception(f"Ollama returned status {r.status_code}: {r.text}")
                except Exception as e:
                    # Fallback if Ollama is not ready/available
                    return {
                        'output': {
                            'error': f"Ollama query failed: {e}",
                            'echo': text,
                            'note': f'Ensure Ollama is running and {vlm_model} is pulled.'
                        },
                        'usage': {'tokens_in': len(text.split()), 'cost': 0.0}
                    }
            raise ValueError(f"Unknown action: {action}")

        client = AgentOS()
        try:
            client.run(manifest=manifest, handler=handler)
        except KeyboardInterrupt:
            self.stdout.write('Disconnected.')
