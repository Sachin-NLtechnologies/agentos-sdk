FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Replicate monorepo layout so that local editable sdk resolves
COPY agentos_sdk /app/agentos_sdk
COPY __AGENT_ID__/backend /app/__AGENT_ID__/backend

WORKDIR /app/__AGENT_ID__/backend
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED=1
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
