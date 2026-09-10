import os
import glob

def fix_file(path):
    with open(path, 'r') as f:
        content = f.read()
    new_content = content.replace("agentos-${AGENT_SLUG}", "${AGENT_SLUG}")
    if new_content != content:
        with open(path, 'w') as f:
            f.write(new_content)
        print(f"Fixed {path}")

for root, _, files in os.walk(r'E:\Users\Sachin\Projects\LLM\LLM\agentos_sdk\agentos_sdk\templates'):
    for f in files:
        if 'docker-compose' in f:
            fix_file(os.path.join(root, f))
