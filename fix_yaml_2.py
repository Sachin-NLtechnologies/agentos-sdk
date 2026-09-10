import sys, re

def update_workflow(path):
    with open(path, 'r') as f:
        content = f.read()

    # Find the broken step and replace it
    broken_step = """            - name: Set lower case repository name
        run: |
          echo "IMAGE_NAME_BACKEND=ghcr.io/-backend" >> 
          echo "IMAGE_NAME_FRONTEND=ghcr.io/-frontend" >> """
    
    correct_step = """      - name: Set lower case repository name
        run: |
          echo "IMAGE_NAME_BACKEND=ghcr.io/${GITHUB_REPOSITORY,,}-backend" >> $GITHUB_ENV
          echo "IMAGE_NAME_FRONTEND=ghcr.io/${GITHUB_REPOSITORY,,}-frontend" >> $GITHUB_ENV"""

    content = content.replace(broken_step, correct_step)

    with open(path, 'w') as f:
        f.write(content)

update_workflow(r'E:\Users\Sachin\Projects\LLM\LLM\agentos_sdk\agentos_sdk\templates\full\.github\workflows\release.yml')
update_workflow(r'E:\Users\Sachin\Projects\LLM\LLM\agentos_sdk\agentos_sdk\templates\full-ai\.github\workflows\release.yml')
