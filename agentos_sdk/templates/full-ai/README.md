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

## Customise

Edit `backend/__PKG__/accounts/management/commands/connect_platform.py` — handler logic, actions, model choice (`VLM_MODEL` env var, default `qwen2.5vl:3b`).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Build fails `../../agentos_sdk not found` | Wrong template version — install SDK ≥ v0.2.1 and re-scaffold |
| Agent stuck QUEUED after Run | `AGENTOS_AGENT_ID` in `.env` doesn't match agent record — provision again |
| Ollama action returns error | Model still pulling — check `docker compose logs ollama-pull` |
| `ERR_EMPTY_RESPONSE` on Open | Restart frontend: `docker compose restart frontend` |
| CORS / CSRF errors | `CSRF_TRUSTED_ORIGINS` in `.env` must include `http://localhost:AGENT_PORT` |
| `agentos: command not found` | Use `python -m agentos_sdk` — the script isn't on PATH yet |
