import os
import re

def fix_file(path):
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # If they manually hardcoded u_z3xmhj3b as a variable, revert it
    content = re.sub(r'\$\{?u_z3xmhj3b\}?', '${AGENT_SLUG}', content, flags=re.IGNORECASE)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

fix_file("docker-compose.prod.yml")
fix_file("client/docker-compose.prod.yml")
