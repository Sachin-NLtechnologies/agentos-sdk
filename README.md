# AgentOS SDK

Official Python SDK for integrating your custom AI agents with AgentOS.

## Installation

```bash
pip install agentos-sdk
```

*(For private or internal usage, you can install directly from the repository using `pip install git+<repo-url>` or by building and sharing a wheel `.whl` file.)*

## Usage

```python
import os
from agentos_sdk import AgentOS

def my_handler(action, payload):
    print(f"Executing {action} with {payload}")
    return {"success": True, "data": "Results from agent"}

client = AgentOS(url=os.getenv("AGENTOS_URL"), key=os.getenv("AGENTOS_KEY"))

manifest = {
    "agent_id": "my_agent",
    "version": "1.0.0",
    "team": "My Team",
    "capabilities": ["do_work"],
    "actions": [{"label": "Do work", "action": "DO_WORK"}],
    "ui_url": "http://localhost:3000"
}

client.run(manifest=manifest, handler=my_handler)
```
