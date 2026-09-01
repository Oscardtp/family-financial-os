---
name: docker-patterns
description: Docker and Docker Compose patterns for local development, container security, networking, volumes, and multi-service orchestration. Use when creating or reviewing Dockerfiles and Compose services, or planning deployment.
---

# Docker Patterns

Docker and Docker Compose best practices for containerized development.

## Docker Compose for Local Development

```yaml
services:
  app:
    build:
      context: .
      target: dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - /app/__pycache__
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/app_dev
    depends_on:
      db:
        condition: service_healthy
    command: uvicorn app.main:app --reload --host 0.0.0.0

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app_dev
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  pgdata:
```

## Multi-Stage Dockerfile (Python)

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

FROM python:3.12-slim AS runner
WORKDIR /app
RUN useradd -r -u 1001 appuser
USER appuser
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Container Security

- Use specific version tags (never `:latest`)
- Run as non-root user
- Drop capabilities: `cap_drop: [ALL]`
- Read-only root filesystem where possible
- No secrets in image layers (use env vars or Docker secrets)
- Use `.dockerignore`

## Networking

Services in the same Compose network resolve by service name:
```
postgres://postgres:postgres@db:5432/app_dev
```

## .dockerignore

```
.git
.env
.env.*
__pycache__
*.pyc
.venv
node_modules
dist
coverage
*.log
tests/
```
