---
name: deployment-patterns
description: Deployment workflows, CI/CD pipeline patterns, Docker containerization, health checks, rollback strategies, and production readiness checklists for web applications. Use when setting up CI/CD, containerizing an app, or checking production readiness before a release.
metadata:
  origin: ECC
---

# Deployment Patterns

Production deployment workflows and CI/CD best practices.

## Deployment Strategies

### Rolling Deployment (Default)
Replace instances gradually — old and new versions run simultaneously.

### Blue-Green Deployment
Run two identical environments. Switch traffic atomically. Instant rollback.

### Canary Deployment
Route small percentage of traffic to new version first. Catches issues with real traffic.

## CI/CD Pipeline (GitHub Actions)

```yaml
name: CI/CD
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest --cov=backend --cov-report=term-missing

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
```

## Health Checks

```python
@app.get("/health")
async def health():
    return {"status": "ok"}
```

## Twelve-Factor App

All config via environment variables — never in code.

## Production Readiness Checklist

### Application
- [ ] All tests pass
- [ ] No hardcoded secrets
- [ ] Error handling covers edge cases
- [ ] Structured logging, no PII
- [ ] Health check endpoint

### Infrastructure
- [ ] Docker image builds reproducibly
- [ ] Environment variables validated at startup
- [ ] Resource limits set
- [ ] SSL/TLS enabled

### Security
- [ ] Dependencies scanned for CVEs
- [ ] CORS configured
- [ ] Rate limiting enabled
- [ ] Auth and authorization verified

### Operations
- [ ] Rollback plan documented
- [ ] Database migration tested
- [ ] Runbook for failure scenarios
