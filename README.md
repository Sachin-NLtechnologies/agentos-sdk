# AgentOS SDK

Official Python SDK for integrating your custom AI agents with AgentOS.

## Installation

```bash
pip install nl-agentos-sdk
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

## Release Checklist

This package uses PyPI Trusted Publishing via GitHub Actions. To release a new version:

1. **Update Version**: Bump `version = "X.Y.Z"` in `pyproject.toml`.
2. **Commit**: Commit your changes.
3. **Tag & Push**:
   ```bash
   git tag vX.Y.Z
   git push origin master --tags
   ```
4. **Publish**: The GitHub Action `.github/workflows/pypi-publish.yml` will automatically build the wheel and publish to PyPI using OIDC!

**Initial PyPI Setup (Trusted Publishing)**
If you are deploying this for the first time, you must configure PyPI to trust this repository:
1. Go to pypi.org > Manage > Publishing.
2. Add a new "GitHub" publisher.
3. Set the repository name (`Sachin-NLtechnologies/agentos-sdk`), workflow filename (`pypi-publish.yml`), and environment name (`pypi`).
4. (No API tokens required to be stored in GitHub Secrets!)
