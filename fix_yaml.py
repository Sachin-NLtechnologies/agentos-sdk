import sys, re

def update_workflow(path):
    with open(path, 'r') as f:
        content = f.read()

    # Remove the hardcoded env vars
    content = re.sub(r'\s+IMAGE_NAME_BACKEND: ghcr.io/\$\{\{ github\.repository \}\}-backend\n', '\n', content)
    content = re.sub(r'\s+IMAGE_NAME_FRONTEND: ghcr.io/\$\{\{ github\.repository \}\}-frontend\n', '\n', content)

    # Insert a step to lowercase the names before docker build
    step_str = '''      - name: Set lower case repository name
        run: |
          echo "IMAGE_NAME_BACKEND=ghcr.io/-backend" >> 
          echo "IMAGE_NAME_FRONTEND=ghcr.io/-frontend" >> 
'''
    content = content.replace('- name: Set up Docker Buildx', step_str + '      - name: Set up Docker Buildx')

    with open(path, 'w') as f:
        f.write(content)

update_workflow(r'E:\Users\Sachin\Projects\LLM\LLM\agentos_sdk\agentos_sdk\templates\full\.github\workflows\release.yml')
update_workflow(r'E:\Users\Sachin\Projects\LLM\LLM\agentos_sdk\agentos_sdk\templates\full-ai\.github\workflows\release.yml')
