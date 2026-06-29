# Build & register a full-AI agent (Django + React/TS + Ollama)

Step-by-step. You run each step; ask me on any doubt. This makes a NEW agent, connects it to the AgentOS
platform, and runs an Ollama-backed action through the platform's **Run** button.

> Mental model: your agent **dials** the platform (register → heartbeat → poll jobs → callback). Platform never
> calls in. Two secrets glue them: the **API key** (`aos_…`) and the **agent_id** — both come from *provision*.

---

## 0. Prerequisites (once)
```bash
# platform must be up on :8088
cd agentOS && docker compose up -d        # if not already running

# install the CLI + SDK from GitHub (public repo)
pip install "agentos-sdk @ git+https://github.com/Sachin-NLtechnologies/agentos-sdk.git@v0.2.0"
agentos --help        # should list: login / status / run / new
```
Also need: Docker, and (recommended) an NVIDIA GPU for Ollama — CPU works but slow.

---

## 1. Provision the agent on the platform (get the `.env`)
This creates the Agent row + API key + OIDC app and hands back a ready `.env`.

- Platform UI → **New agent**. Pick:
  - **name**: lowercase, no spaces, e.g. `arnotes` (this becomes `agent_id` — remember it).
  - **redirect_uri**: `http://localhost:3001/auth/callback` (your agent UI origin + `/auth/callback`; change the
    port if you'll use a different one — see step 4).
- It returns an `.env`. **Copy all of it.** It contains:
```
AGENTOS_KEY=aos_...
AGENTOS_URL=http://host.docker.internal:8088
AGENTOS_AGENT_ID=arnotes          # = the name you typed
AGENTOS_UI_URL=http://localhost:3001
AGENTOS_OIDC_ISSUER=http://host.docker.internal:8088
AGENTOS_OIDC_PUBLIC_ISSUER=http://localhost:8088
AGENTOS_CLIENT_ID=...
AGENTOS_CLIENT_SECRET=...
AGENTOS_REDIRECT_URI=http://localhost:3001/auth/callback
AGENTOS_LOGIN_REDIRECT=http://localhost:3001/
```
> No "New agent" button yet? Call provision directly (must be logged-in OWNER/ADMIN):
> `POST http://localhost:8088/api/v1/agents/provision` body `{"name":"arnotes","redirect_uri":"http://localhost:3001/auth/callback"}`.

---

## 2. Scaffold the agent code
```bash
agentos new arnotes --type full-ai --dir .
```
Makes `./arnotes/` with `backend/` (Django), `frontend/` (Vite React TS), `docker-compose.yml`, ollama services.
`__AGENT_ID__`/`__PKG__` are already replaced with `arnotes`.

> Use the SAME name as step 1. If the scaffold name and the provisioned name differ, jobs won't route (the
> classic mismatch bug). The `AGENTOS_AGENT_ID` env makes the connector follow the `.env`, so keeping both
> `arnotes` is all you need.

---

## 3. Drop in the `.env`
Save the step-1 text as `./arnotes/.env`.

If port 3001 is taken (another agent), set a unique port — add/edit in `.env`:
```
AGENT_PORT=3003
AGENTOS_UI_URL=http://localhost:3003
AGENTOS_REDIRECT_URI=http://localhost:3003/auth/callback
AGENTOS_LOGIN_REDIRECT=http://localhost:3003/
VLM_MODEL=qwen2.5vl:3b        # no dash. leave default unless you pulled another model
CSRF_COOKIE_NAME=arnotes_csrftoken   # unique per agent — avoids localhost cookie collision
```
(If you changed the port, also update the OAuth app's redirect in the platform, or re-provision with the new
redirect_uri — OIDC login fails if they don't match.)

---

## 4. Write the agent's brain (the only real coding)
Open `arnotes/backend/<pkg>/accounts/management/commands/connect_platform.py`. Two parts:

**a) Manifest** — declare what the agent offers (shows as Run buttons on the platform):
```python
manifest = {
    'agent_id': os.getenv('AGENTOS_AGENT_ID', 'arnotes'),
    'version': '1.0.0',
    'team': 'core',
    'capabilities': ['summarize'],
    'actions': [
        {'label': 'Summarize text', 'action': 'SUMMARIZE'},
    ],
    'ui_url': os.getenv('AGENTOS_UI_URL', 'http://localhost:3001'),
}
```

**b) Handler** — given an action, do work (call Ollama here), return `{output, usage}`:
```python
def handler(action, payload):
    action = (action or '').upper()
    if action == 'SUMMARIZE':
        text = payload.get('text', '')
        ollama = os.getenv('OLLAMA_URL', 'http://ollama:11434')
        r = requests.post(f"{ollama}/api/chat", json={
            "model": os.getenv('VLM_MODEL', 'qwen2.5vl:3b'),   # no dash
            "messages": [{"role": "user", "content": f"Summarize:\n{text}"}],
            "stream": False,
            "keep_alive": "30m",
        }, timeout=(10, 600))
        r.raise_for_status()
        ans = r.json().get('message', {}).get('content', '')
        return {'output': {'summary': ans},
                'usage': {'tokens_in': len(text.split()), 'tokens_out': len(ans.split()), 'cost': 0.0}}
    raise ValueError(f'unknown action: {action}')
```
Everything else (register/heartbeat/poll/callback) the SDK does — don't touch it.

---

## 5. Bring it up
```bash
cd arnotes
docker compose --env-file .env up -d --build
docker compose --env-file .env logs -f ollama-pull   # first run pulls qwen2.5vl:3b (slow once); wait for done
```
Services: `backend` (Django, internal 8000), `frontend` (your port), `connector` (runs connect_platform), `ollama`, `ollama-pull`.

---

## 6. Verify registration end-to-end
```bash
# connector says it registered
docker compose --env-file .env logs --tail=20 connector      # -> "Registered as arnotes"
```
On the platform:
1. Dashboard → **arnotes = ONLINE** (green; heartbeat < 60s).
2. **Open** → loads the agent UI at your port.
3. **Run** the `Summarize text` action with input `{"text":"..."}` → job QUEUED → RUNNING → **success** with the
   Ollama summary. (Not stuck = the id match + Ollama tag are correct.)

DB cross-check (optional):
```bash
docker compose -f agentOS/docker-compose.yml exec backend python manage.py shell -c "
from apps.registry.models import Agent
print([(a.agent_id, a.last_seen) for a in Agent.objects.all()])"
```

---

## 7. The Django + TypeScript SSO part ("Login with AgentOS")
The full-ai template already wires it from the `.env`:
- **Backend**: uses `AGENTOS_CLIENT_ID/SECRET/REDIRECT_URI` + `agentos_sdk.django_auth` for the server-side OIDC
  callback. Make sure platform OAuth app is `algorithm="RS256"` (provision sets it) and the platform has
  `OIDC_RSA_PRIVATE_KEY` set.
- **Frontend (TS)**: `frontend/src/pages/Login.tsx` has the "Login with AgentOS" button → platform login →
  `redirect_uri` → back into the agent. To customize the dashboard/results UI, edit
  `frontend/src/pages/Dashboard.tsx` + `frontend/src/api/apiClient.ts` (set `xsrfCookieName` to your
  `CSRF_COOKIE_NAME`).

---

## Troubleshooting (the bugs we already hit — fixes baked in)
| Symptom | Cause | Fix |
|---|---|---|
| Agent shows **Offline** but containers up | wrong `AGENTOS_URL` | must be `http://host.docker.internal:8088` (in `.env`) |
| Tile online but **Run** job stuck `QUEUED` | agent_id mismatch (provision name ≠ manifest) | keep both = same name; `AGENTOS_AGENT_ID` drives it |
| Every action **"Ollama connection error"** | wrong model tag | `qwen2.5vl:3b` (NO dash); set `VLM_MODEL` |
| Docker build fails on `pip install git+...` | SDK repo private | repo is public — re-check the URL/tag `@v0.2.0` |
| Code change not showing | image is stale (source COPYed at build) | rebuild with `--build` (or `--no-cache`) |
| Two agents both grab 3001 | port clash | unique `AGENT_PORT` + `AGENTOS_UI_URL` per agent |
| SSO 500 at `/o/token/` | OAuth app `algorithm` empty | set `RS256`; platform needs `OIDC_RSA_PRIVATE_KEY` |
| SSO 403 / CSRF | shared cookie name on localhost | unique `CSRF_COOKIE_NAME=arnotes_csrftoken` |

---

## Recap (the whole loop)
```
New agent on platform  →  copy .env
agentos new arnotes --type full-ai
drop .env  →  edit manifest + handler (Ollama)
docker compose --env-file .env up -d --build
connector → register + heartbeat → ONLINE
Run on platform → job → handler(Ollama) → callback → result
```
Ask me at whatever step trips up — paste the connector log + the symptom and I'll pin it.
