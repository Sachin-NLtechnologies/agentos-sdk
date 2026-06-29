import os, sys, json, time, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

BASE = "/tmp/build"
if not os.path.exists(BASE):
    BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path[:0] = [os.path.join(BASE, "agentos_sdk"), os.path.join(BASE, "agents/summarizer"), os.path.join(BASE, "agents/scribe")]

import agentos_sdk
from agentos_sdk import AgentOS, config as C
import summarizer, scribe

ok = 0; fail = 0
def check(name, cond):
    global ok, fail
    if cond: ok += 1; print(f"  PASS {name}")
    else: fail += 1; print(f"  FAIL {name}")

print("== unit: summarizer ==")
SAMPLE = ("AgentOS is a control plane. Agents dial out to the platform. "
          "The platform tracks usage and jobs. Usage is central like OpenAI. "
          "Agents report tokens in the callback.")
res = summarizer.dispatch("SUMMARIZE", {"text": SAMPLE, "max_sentences": 2})
check("returns output+usage keys", set(res) == {"output", "usage"})
check("summary nonempty", bool(res["output"]["summary"]))
check("bullets <=2", len(res["output"]["bullets"]) <= 2)
check("usage tokens_in>0", res["usage"]["tokens_in"] > 0)
try:
    summarizer.dispatch("NOPE", {}); check("unknown raises", False)
except ValueError: check("unknown raises", True)

print("== unit: scribe (stub fallback, no whisper) ==")
rs = scribe.dispatch("TRANSCRIBE", {"audio_b64": __import__("base64").b64encode(b"x").decode()})
check("scribe output+usage", set(rs) == {"output", "usage"})
check("scribe transcript present", "transcript" in rs["output"])

print("== unit: SDK _split ==")
o, u = AgentOS._split({"output": {"a": 1}, "usage": {"t": 2}})
check("standard split", o == {"a": 1} and u == {"t": 2})
o2, u2 = AgentOS._split({"success": True})       # legacy ReceivIQ-style
check("legacy split (no usage)", o2 == {"success": True} and u2 == {})

print("== unit: config precedence ==")
C.save_credentials("http://creds:1", "aos_creds")
os.chdir(os.path.join(BASE, "agents/summarizer"))
r = C.resolve("agentos.toml")
check("package from toml", r["package"] == "summarizer")
check("url from toml over creds", r["url"] == "http://localhost:8088")
os.environ["AGENTOS_URL"] = "http://env:9"; os.environ["AGENTOS_KEY"] = "aos_env"
r2 = C.resolve("agentos.toml")
check("env beats toml", r2["url"] == "http://env:9" and r2["key"] == "aos_env")
del os.environ["AGENTOS_URL"]; del os.environ["AGENTOS_KEY"]

print("== unit: cli.load_agent ==")
from agentos_sdk import cli
m, d = cli.load_agent("summarizer")
check("loads manifest+dispatch", m["agent_id"] == "summarizer" and callable(d))

print("== integration: fake platform, full loop ==")
CB = {}
JOB = {"id": "job1", "action": "SUMMARIZE", "input": {"text": SAMPLE, "max_sentences": 2}}
served = {"jobs_served": False}

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, body=b"{}"):
        self.send_response(code); self.send_header("Content-Type","application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_POST(self):
        ln = int(self.headers.get("Content-Length", 0)); raw = self.rfile.read(ln) if ln else b"{}"
        if self.path.endswith("/register"): self._send(200, b'{"agent_id":"summarizer"}')
        elif self.path.endswith("/heartbeat"): self._send(200)
        elif "/callback" in self.path:
            CB.update(json.loads(raw)); self._send(200)
        else: self._send(404)
    def do_GET(self):
        if self.path.endswith("/jobs"):
            if not served["jobs_served"]:
                served["jobs_served"] = True
                self._send(200, json.dumps([JOB]).encode())
            else:
                self._send(200, b"[]")
        else: self._send(404)

srv = HTTPServer(("127.0.0.1", 8099), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()

client = AgentOS(url="http://127.0.0.1:8099", key="aos_test")
threading.Thread(target=lambda: client.run(summarizer.MANIFEST, summarizer.dispatch), daemon=True).start()

deadline = time.time() + 8
while time.time() < deadline and "status" not in CB:
    time.sleep(0.2)
client.running = False; srv.shutdown()

check("callback received", "status" in CB)
check("callback status success", CB.get("status") == "success")
check("callback has summary", bool(CB.get("output", {}).get("summary")))
check("callback has usage tokens", CB.get("usage", {}).get("tokens_in", 0) > 0)
print(f"\nRESULT: {ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
