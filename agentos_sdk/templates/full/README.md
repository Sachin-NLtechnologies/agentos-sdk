# __AGENT_ID__  (AgentOS full agent)

AgentOS agent with a Django backend + React frontend.

## Setup

> **Run all commands from this directory** (`__AGENT_ID__/`) — not from the parent folder.

1. Copy your provisioned `.env` into this folder:
   ```
   __AGENT_ID__/.env   ← paste the env block from the platform's New Agent dialog
   ```

2. Build and start:
   ```bash
   docker compose --env-file .env up -d --build
   ```

3. Watch the connector register:
   ```bash
   docker compose logs -f connector
   # expect: [agentos-sdk] Registered as __AGENT_ID__
   ```

4. Platform dashboard → **`__AGENT_ID__`** turns **ONLINE** within ~30s → **Open** opens the UI → **Run** executes an action.

## Customise

Edit the action handler in `backend/__PKG__/accounts/management/commands/connect_platform.py`.

## Ports

The UI runs on `AGENT_PORT` (from your `.env`). If two agents clash, change `AGENT_PORT` in the `.env` and re-`up`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Build fails `../../agentos_sdk not found` | Wrong template version — install SDK ≥ v0.2.1 and re-scaffold |
| Agent stuck QUEUED after Run | `AGENTOS_AGENT_ID` in `.env` doesn't match agent record — provision again |
| `ERR_EMPTY_RESPONSE` on Open | Restart frontend: `docker compose restart frontend` |
| CORS / CSRF errors | `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` in `.env` must include `http://localhost:AGENT_PORT` |
| `agentos: command not found` | Use `python -m agentos_sdk` — the script isn't on PATH |
