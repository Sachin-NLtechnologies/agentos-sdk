#!/bin/bash
set -e

read -p "Enter GHCR Username (lowercase): " GHCR_USER
read -s -p "Enter GHCR PAT (read:packages): " GHCR_PAT
echo ""

GHCR_USER=$(echo "$GHCR_USER" | tr '[:upper:]' '[:lower:]')

echo "$GHCR_PAT" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

docker network create agentos-net 2>/dev/null || true

MAX_RETRIES=3
RETRY_COUNT=0
SUCCESS=false

while [ "$SUCCESS" = false ] && [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker compose -f docker-compose.prod.yml pull; then
        SUCCESS=true
    else
        RETRY_COUNT=$((RETRY_COUNT+1))
        echo "Pull failed (attempt $RETRY_COUNT of $MAX_RETRIES). Retrying in 5 seconds..."
        sleep 5
    fi
done

if [ "$SUCCESS" = false ]; then
    echo "Docker compose pull failed after $MAX_RETRIES attempts."
    exit 1
fi

docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate --noinput

touch .env
if ! grep -q "^GHCR_USER=" .env; then
    echo "GHCR_USER=$GHCR_USER" >> .env
else
    sed -i "s/^GHCR_USER=.*/GHCR_USER=$GHCR_USER/" .env
fi

if ! grep -q "^GHCR_PAT=" .env; then
    echo "GHCR_PAT=$GHCR_PAT" >> .env
else
    sed -i "s/^GHCR_PAT=.*/GHCR_PAT=$GHCR_PAT/" .env
fi

echo "Deployment completed."
