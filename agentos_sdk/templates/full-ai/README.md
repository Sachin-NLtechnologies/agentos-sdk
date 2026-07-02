# __AGENT_ID__  (AgentOS full-AI agent)

AgentOS agent with a Django backend, React frontend, and local Ollama VLM.

## Setup

> **Run all commands from this directory** (`__AGENT_ID__/`) — not from the parent folder.

1. Copy your provisioned `.env` into this folder:
   ```
   __AGENT_ID__/.env   ← paste the env block from the platform's New Agent dialog
   ```

2. Build and start (first run pulls the Ollama model — may take a few minutes):
   ```bash
   docker compose --env-file .env up -d --build
   ```

3. Watch the connector register:
   ```bash
   docker compose logs -f connector
   # expect: [agentos-sdk] Registered as __AGENT_ID__
   ```

4. Platform dashboard → **`__AGENT_ID__`** turns **ONLINE** within ~30s → **Open** opens the UI → **Run** executes an action.

## Ports

The UI runs on `AGENT_PORT` (from your `.env`, auto-assigned by provision so agents don't clash). Edit `.env` to override.

## Actions — what shows up as "Run" on the platform

Runnable actions come from manifest['actions'] in
backend/__PKG__/accounts/management/commands/connect_platform.py:
    'actions': [ {'label': 'Summarize text', 'action': 'SUMMARIZE'} ]

Each becomes a Run button on your agent's page. Clicking it sends {action, input} to
handler(action, payload); whatever you return as `output` shows back on the platform.

Add one: 1) add {'label','action'} to actions  2) add `if action=='X':` in handler,
return {'output':{...},'usage':{...}}  3) restart the agent -> it re-registers, button appears.
Inputs: platform passes a JSON `input`; read keys from `payload` (e.g. payload.get('text')).
Document your expected keys here. You never touch platform code.

## Local HTTPS Certs

This agent serves the browser UI over mkcert HTTPS. On each host, create the local cert files before starting the frontend:

```bash
mkdir -p ../certs
mkcert -cert-file ../certs/cert.pem -key-file ../certs/key.pem vbsagent 192.168.1.50 localhost 127.0.0.1 host.docker.internal
```

The cert files are host-local secrets and are intentionally not committed. If the frontend exits with `/certs/key.pem` missing, generate the certs above and run:

```bash
docker compose --env-file .env up -d --build frontend
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Build fails `../../agentos_sdk not found` | Wrong template version — install SDK ≥ v0.2.1 and re-scaffold |
| Agent stuck QUEUED after Run | `AGENTOS_AGENT_ID` in `.env` doesn't match agent record — provision again |
| Ollama action returns error | Model still pulling — check `docker compose logs ollama-pull` |
| `ERR_EMPTY_RESPONSE` on Open | Restart frontend: `docker compose restart frontend` |
| CORS / CSRF errors | `CSRF_TRUSTED_ORIGINS` in `.env` must include `http://localhost:AGENT_PORT` |
| `agentos: command not found` | Use `python -m agentos_sdk` — the script isn't on PATH yet |
