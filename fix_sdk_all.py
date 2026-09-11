import re
import os

def fix_file(path):
    with open(path, 'r') as f:
        content = f.read()

    # 1. Remove agentos- prefix
    content = content.replace("agentos-${AGENT_SLUG}", "${AGENT_SLUG}")

    # 2. Remove worker, beat, redis blocks
    # Match from "  worker:" to the next "  [a-z]" or end of string
    content = re.sub(r'\n  worker:.*?(?=\n  [a-z_]+:|\Z)', '', content, flags=re.DOTALL)
    content = re.sub(r'\n  beat:.*?(?=\n  [a-z_]+:|\Z)', '', content, flags=re.DOTALL)
    content = re.sub(r'\n  redis:.*?(?=\n  [a-z_]+:|\Z)', '', content, flags=re.DOTALL)
    content = re.sub(r'\n  redis_data:[\s]*', '\n', content)

    # 3. Add DATABASE_URL to backend environment if not present
    if "client" in path and "DATABASE_URL" not in content:
        # Find backend: block and insert after env_file: .env
        content = content.replace("    env_file: .env\n", "    env_file: .env\n    environment:\n      - DATABASE_URL=postgres://${POSTGRES_USER:-__PKG__}:${POSTGRES_PASSWORD}@__PKG___db:5432/${POSTGRES_DB:-__PKG__}\n", 1)

    with open(path, 'w') as f:
        f.write(content)
    print(f"Fixed {path}")

fix_file(r'E:\Users\Sachin\Projects\LLM\LLM\agentos_sdk\agentos_sdk\templates\full\docker-compose.prod.yml')
fix_file(r'E:\Users\Sachin\Projects\LLM\LLM\agentos_sdk\agentos_sdk\templates\full\client\docker-compose.prod.yml')
fix_file(r'E:\Users\Sachin\Projects\LLM\LLM\agentos_sdk\agentos_sdk\templates\full-ai\docker-compose.prod.yml')
fix_file(r'E:\Users\Sachin\Projects\LLM\LLM\agentos_sdk\agentos_sdk\templates\full-ai\client\docker-compose.prod.yml')
