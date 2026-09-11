import os

def fix_file(path):
    with open(path, 'r') as f:
        content = f.read()
    new_content = content.replace("${{ vars.AGENT_SLUG }}", "__SLUG__")
    if new_content != content:
        with open(path, 'w') as f:
            f.write(new_content)
        print(f"Fixed {path}")

fix_file(r'E:\Users\Sachin\Projects\LLM\LLM\agentos_sdk\agentos_sdk\templates\full\.github\workflows\release.yml')
fix_file(r'E:\Users\Sachin\Projects\LLM\LLM\agentos_sdk\agentos_sdk\templates\full-ai\.github\workflows\release.yml')
