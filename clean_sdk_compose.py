import os

def clean_compose(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    skip = False
    for line in lines:
        if line.strip().startswith('redis:') or line.strip().startswith('worker:') or line.strip().startswith('beat:'):
            skip = True
        elif skip and line.strip() != '' and not line.startswith('  ') and not line.startswith('\t') and not line.startswith('    ') and not line.startswith('      '):
            skip = False
            
        if line.strip() == 'watchtower:' or line.strip() == '__PKG___db:':
            skip = False
            
        if line.strip() == 'redis_data:':
            continue
            
        if not skip:
            new_lines.append(line)
            
    with open(path, 'w') as f:
        f.writelines(new_lines)
    print(f"Cleaned {path}")

clean_compose(r'E:\Users\Sachin\Projects\LLM\LLM\agentos_sdk\agentos_sdk\templates\full\client\docker-compose.prod.yml')
clean_compose(r'E:\Users\Sachin\Projects\LLM\LLM\agentos_sdk\agentos_sdk\templates\full-ai\client\docker-compose.prod.yml')
