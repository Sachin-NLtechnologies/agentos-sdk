import os
import re

def fix_env():
    if not os.path.exists('.env'): return
    with open('.env', 'rb') as f:
        content = f.read().decode('utf-8')
    
    # Replace CRLF with LF
    content = content.replace('\r\n', '\n')
    
    # Escape $ in SECRET_KEY if not quoted
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('SECRET_KEY='):
            val = line[len('SECRET_KEY='):]
            if not val.startswith("'") and not val.startswith('"'):
                # Escape $ with $$ for docker compose
                val = val.replace('$', '$$')
                lines[i] = f"SECRET_KEY='{val}'"
    
    with open('.env', 'wb') as f:
        f.write('\n'.join(lines).encode('utf-8'))

def write_compose():
    compose = """name: ${AGENT_SLUG}

services:
  backend:
    image: ghcr.io/sachin-nltechnologies/${AGENT_SLUG}-backend:stable
    env_file: .env
    volumes:
      - user_manual_generator_data:/data
      - static_data:/app/staticfiles
      - media_data:/data/media
    networks:
      agentos-net:
        aliases: ["${AGENT_SLUG}-backend"]
    depends_on:
      user_manual_generator_db:
        condition: service_healthy
    restart: always
    labels:
      - "com.centurylinklabs.watchtower.enable=true"

  frontend:
    image: ghcr.io/sachin-nltechnologies/${AGENT_SLUG}-frontend:stable
    environment:
      - AGENT_SLUG=${AGENT_SLUG}
    env_file: .env
    volumes:
      - static_data:/app/staticfiles:ro
      - media_data:/media:ro
    networks:
      agentos-net:
        aliases: ["${AGENT_SLUG}-frontend"]
    restart: always
    labels:
      - "com.centurylinklabs.watchtower.enable=true"

  connector:
    image: ghcr.io/sachin-nltechnologies/${AGENT_SLUG}-backend:stable
    command: ["python", "manage.py", "connect_platform"]
    env_file: .env
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - user_manual_generator_data:/data
    networks:
      agentos-net:
        aliases: ["${AGENT_SLUG}-connector"]
    depends_on:
      user_manual_generator_db:
        condition: service_healthy
    restart: always
    labels:
      - "com.centurylinklabs.watchtower.enable=true"

  watchtower:
    image: ghcr.io/nicholas-fedor/watchtower:latest
    environment:
      - WATCHTOWER_LABEL_ENABLE=true
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_POLL_INTERVAL=300
      - REPO_USER=${GHCR_USER}
      - REPO_PASS=${GHCR_PAT}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - agentos-net
    restart: always

  user_manual_generator_db:
    image: postgres:16
    environment:
      - POSTGRES_DB=${POSTGRES_DB:-user_manual_generator}
      - POSTGRES_USER=${POSTGRES_USER:-user_manual_generator}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - user_manual_generator_pgdata:/var/lib/postgresql/data
    networks:
      - agentos-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-user_manual_generator} -d ${POSTGRES_DB:-user_manual_generator}"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: always
    labels:
      - "com.centurylinklabs.watchtower.enable=false"

volumes:
  user_manual_generator_data:
  user_manual_generator_pgdata:
  media_data:
  static_data:

networks:
  agentos-net:
    external: true
"""
    with open('docker-compose.prod.yml', 'w', encoding='utf-8') as f:
        f.write(compose)

fix_env()
write_compose()
print("Fixed!")
