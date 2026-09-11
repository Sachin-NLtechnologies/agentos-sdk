import os

def add_database_url(path, pkg):
    with open(path, 'r') as f:
        content = f.read()
    
    if "DATABASE_URL" in content:
        return
        
    lines = content.split('\n')
    new_lines = []
    in_backend = False
    in_backend_environment = False
    
    for line in lines:
        if line.strip() == 'backend:':
            in_backend = True
        elif in_backend and line.strip() and not line.startswith('  '):
            in_backend = False
            
        if in_backend and line.strip() == 'env_file: .env':
            new_lines.append(line)
            new_lines.append(f"    environment:\n      - DATABASE_URL=postgres://${{POSTGRES_USER:-{pkg}}}:${{POSTGRES_PASSWORD}}@{pkg}_db:5432/${{POSTGRES_DB:-{pkg}}}")
            continue
            
        new_lines.append(line)
        
    with open(path, 'w') as f:
        f.write('\n'.join(new_lines))
    print(f"Added DATABASE_URL to {path}")

add_database_url(r'E:\Users\Sachin\Projects\LLM\LLM\agentos_sdk\agentos_sdk\templates\full\client\docker-compose.prod.yml', '__PKG__')
add_database_url(r'E:\Users\Sachin\Projects\LLM\LLM\agentos_sdk\agentos_sdk\templates\full-ai\client\docker-compose.prod.yml', '__PKG__')
