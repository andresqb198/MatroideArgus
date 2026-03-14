# Meridian Backend

FastAPI backend for the Meridian AI Ops & Governance Platform.

## Local Development

```bash
docker compose up -d  # Start PostgreSQL + ClickHouse
pip install -e ".[dev]"
uvicorn app.main:app --reload
```
