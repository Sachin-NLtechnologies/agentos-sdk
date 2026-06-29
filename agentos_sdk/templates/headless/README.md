# __AGENT_ID__  (AgentOS headless agent)

A lightweight AgentOS agent with no UI — just a manifest + action handler.

## Setup

```bash
pip install -e .
python -m agentos_sdk login --url http://localhost:8088 --key aos_...
python -m agentos_sdk run
```

The agent registers itself and starts polling for jobs. Check the platform dashboard — `__AGENT_ID__` should appear **ONLINE** within ~30s.

## Customise

Edit `__PKG__/manifest.py` to add capabilities and actions, and `__PKG__/handler.py` / `__PKG__/actions/` to implement them.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `agentos: command not found` | Use `python -m agentos_sdk` instead — the script isn't on PATH yet |
| Agent stuck PENDING | Check `AGENTOS_URL` points to the running platform (`http://localhost:8088`) |
| Auth error / 401 | Run `python -m agentos_sdk login` again with the correct key |
