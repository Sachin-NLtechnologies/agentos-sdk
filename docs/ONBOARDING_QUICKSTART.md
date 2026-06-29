# AgentOS — Create & Register an Agent (Quickstart, SDK v0.2.2)

> **Paste this to ChatGPT before the steps:**
> "You are a first-time third-party developer. The AgentOS platform is already installed and running at
> http://localhost:8088 — you did NOT build it. Follow the steps below EXACTLY, in order. Run each command,
> and after each step record PASS or FAIL and paste the real output. Do not skip steps, do not assume anything
> works, do not invent commands. At the end, fill in the Bug Report Template."

A fresh, self-contained run: install SDK → provision → scaffold → connect → verify ONLINE.

---

## 0. Prerequisites
- Docker Desktop installed and running (`docker ps` works).
- Python 3.10+ (`python --version`).
- Platform reachable: open http://localhost:8088 and log in (OWNER or ADMIN account).
- Internet (Docker pulls images + the SDK from GitHub). full-AI agents bundle Ollama in their own compose.

## 1. Install the SDK + verify the CLI
```bash
pip install "agentos-sdk @ git+https://github.com/Sachin-NLtechnologies/agentos-sdk.git@v0.2.2"
python -m agentos_sdk --help
```
Always invoke as **`python -m agentos_sdk`** — works even if the `agentos` shortcut isn't on PATH.
Expect: a help screen listing `login / status / run / new`. (FAIL here = stop, report.)

## 2. Provision the agent on the platform (creates credentials + `.env`)
- Platform UI → **New agent**.
  - **name**: lowercase, no spaces, e.g. `invoice3` (this becomes the `agent_id` — remember it).
  - **redirect_uri**: leave default (auto-derived) unless you have one.
- Click create → it returns an **`.env`**. **Copy the whole thing.**
- The port is auto-assigned (no 3001 clash) and the `.env` is complete (includes `AGENT_PORT`, `ALLOWED_HOSTS`,
  `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`, OIDC vars).

## 3. Scaffold the project
```bash
python -m agentos_sdk new invoice3 --type full-ai
```
Use the SAME name as step 2. Creates `./invoice3/` (Django backend + React/TS frontend + connector + Ollama).
It prints type-aware next steps.

## 4. Drop in the `.env`
Save the step-2 text as **`invoice3/.env`** (exact name).

## 5. Start it (from INSIDE the folder)
```bash
cd invoice3
docker compose --env-file .env up -d --build
docker compose --env-file .env logs -f ollama-pull   # first run pulls qwen2.5vl:3b (slow once); Ctrl+C when "success"
```
> Must run from inside `invoice3/` — compose reads `invoice3/.env`, not the parent folder.

## 6. Verify registration end-to-end
```bash
docker compose --env-file .env logs --tail=20 connector     # expect: "Registered as invoice3"
```
On the platform:
1. Dashboard → **invoice3 = ONLINE** (green, within ~30s).
2. **Open** → the agent UI loads (on its assigned port).
3. **Run** the example action → job goes QUEUED → RUNNING → **success** with output.

That's a fully registered, working agent.

## 7. (Optional) make it do your thing
Edit `invoice3/backend/<pkg>/accounts/management/commands/connect_platform.py`:
- **manifest** `actions` = the buttons shown on the platform.
- **handler(action, payload)** = the logic (call Ollama, your APIs, etc.), return `{output, usage}`.
Then `docker compose --env-file .env up -d --build` again.

---

## Troubleshooting (quick)
| Symptom | Fix |
|---|---|
| `agentos` not recognized | use `python -m agentos_sdk ...` |
| Docker build can't find SDK / `COPY agentos_sdk` | you're on an old tag — reinstall `@v0.2.2` and re-scaffold |
| compose can't find `.env` | you're in the wrong dir — `cd invoice3` first |
| agent ONLINE but Run stuck QUEUED | agent_id mismatch — scaffold name must equal provisioned name |
| "Ollama connection error" | wait for `ollama-pull` to finish; model tag must be `qwen2.5vl:3b` (no dash) |
| port already in use | provision auto-picks a free port — make sure you used the freshly provisioned `.env` |

---

## Bug Report Template (fill and send back)
```
SDK version tested: v0.2.2

| Stage                  | PASS/FAIL | Notes / output |
|------------------------|-----------|----------------|
| 0 Prerequisites        |           |                |
| 1 SDK install + --help |           |                |
| 2 Provision (.env)     |           |                |
| 3 Scaffold (new)       |           |                |
| 4 Place .env           |           |                |
| 5 docker compose up    |           |                |
| 6a connector Registered|           |                |
| 6b dashboard ONLINE    |           |                |
| 6c Run action success  |           |                |
| 7 SSO login (if tried) |           |                |

First blocking issue (if any):
Exact error text:
Step where it happened:
Suggested cause:
```
```
