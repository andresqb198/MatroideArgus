# Meridian — AI Ops & Governance Platform

## Monorepo Layout (uv workspace)
- `packages/meridian-sdk/` — Python SDK (`pip install meridian-sdk`). The `@observe` decorator instruments ML model predict() calls with < 2ms p99 overhead.
- `packages/meridian-api/` — FastAPI backend. Ingests predictions, serves dashboards, handles auth (Auth0 SSO + RBAC), multi-tenant via PostgreSQL schema-per-tenant.
- `infra/db/migrations/` — Alembic migrations for PostgreSQL.
- `infra/db/clickhouse/` — ClickHouse DDL for prediction storage (50B rows, 2-year retention).
- `docker/` — Docker Compose for local dev (PostgreSQL 16 + ClickHouse 24 + API).
- `docs/` — Documentation.

## Tech Stack
- **Language**: Python 3.12+
- **Package manager**: uv (workspace monorepo)
- **API framework**: FastAPI + Uvicorn
- **ORM**: SQLAlchemy 2.0 (async) + Pydantic
- **Databases**: PostgreSQL 16 (OLTP, multi-tenant), ClickHouse 24 (predictions OLAP)
- **Auth**: Auth0 (SAML 2.0 / OIDC), RBAC with 4 roles
- **Linter/Formatter**: ruff
- **Type checker**: mypy
- **Tests**: pytest + pytest-asyncio + httpx

## Key Commands
```bash
uv sync                              # Install all deps
uv run pytest                        # Run all tests
uv run ruff check .                  # Lint
uv run ruff format .                 # Format
uv run uvicorn meridian_api.main:app --reload  # Run API locally
docker compose -f docker/docker-compose.yml up -d  # Start infra
uv run alembic -c infra/db/migrations/alembic.ini upgrade head  # Run migrations
```

## Architecture Decisions
- src layout for all packages (prevents import shadowing)
- Async-first: all I/O is async (asyncpg, httpx)
- Multi-tenant via PostgreSQL schema separation (one schema per tenant)
- ClickHouse for high-volume prediction storage (append-only, partitioned by month)
- SDK sends predictions async via background thread with local buffer
- All API endpoints versioned under `/v1/`
- Audit trail: append-only table, immutable logs

## NFR Targets (MVP)
- SDK decorator overhead: < 2ms p99
- Dashboard initial load: < 3s
- API supports 10K predictions/sec per tenant
- Code coverage: >= 80%
- All data encrypted at rest (AES-256) and in transit (TLS 1.3)

## Requirements
Full requirements document: `/home/andresqb/Documents/meridian-requirements.pdf`
