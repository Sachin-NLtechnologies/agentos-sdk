import os, json
from pathlib import Path

# toml reader: stdlib tomllib (py3.11+), else tomli, else a tiny fallback for our simple files
try:
    import tomllib as _toml
    def _loads(s): return _toml.loads(s)
except ModuleNotFoundError:
    try:
        import tomli as _toml
        def _loads(s): return _toml.loads(s)
    except ModuleNotFoundError:
        import re
        def _loads(s):
            data, section = {}, None
            for line in s.splitlines():
                line = line.split('#', 1)[0].strip()
                if not line: continue
                m = re.match(r'^\[(.+)\]$', line)
                if m:
                    section = m.group(1).strip(); data.setdefault(section, {}); continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    v = v.strip().strip('"').strip("'")
                    (data[section] if section else data)[k.strip()] = v
            return data

CRED = Path.home() / '.agentos' / 'credentials.json'

def save_credentials(url, key):
    CRED.parent.mkdir(parents=True, exist_ok=True)
    CRED.write_text(json.dumps({'url': url, 'key': key}, indent=2))
    try: os.chmod(CRED, 0o600)
    except Exception: pass
    return CRED

def _creds():
    if CRED.exists():
        try: return json.loads(CRED.read_text())
        except Exception: return {}
    return {}

def load_agent_config(path='agentos.toml'):
    p = Path(path)
    return _loads(p.read_text()) if p.exists() else {}

def resolve(path='agentos.toml'):
    cfg = load_agent_config(path); creds = _creds()
    plat = cfg.get('platform', {})
    url = os.getenv('AGENTOS_URL') or plat.get('url') or creds.get('url') or 'http://localhost:8080'
    key = os.getenv('AGENTOS_KEY') or creds.get('key') or ''
    package = (cfg.get('agent') or {}).get('package')
    return {'url': url.rstrip('/'), 'key': key, 'package': package}
