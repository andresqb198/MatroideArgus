# Meridian — AI Ops & Governance Platform

## Project Structure (Monorepo)
- `sdk/` — Python SDK (`meridian-sdk` on PyPI)
- `backend/` — FastAPI backend API
- `dashboard/` — Web dashboard (TBD: Next.js or similar)
- `infrastructure/` — Docker, K8s manifests, IaC
- `docs/` — Documentation

## Tech Stack
- **SDK**: Python 3.10+, minimal dependencies
- **Backend**: FastAPI, SQLAlchemy, Alembic, PostgreSQL, ClickHouse
- **Auth**: Auth0 (SAML 2.0, OIDC), RBAC with 4 roles (Admin, ML Engineer, Compliance Officer, Viewer)
- **Infra**: Docker Compose (local), Kubernetes (prod)

## Key Commands
```bash
# Local development
docker compose up -d                    # Start PostgreSQL + ClickHouse
cd sdk && pip install -e ".[dev]"       # Install SDK in dev mode
cd backend && pip install -e ".[dev]"   # Install backend in dev mode
cd backend && uvicorn app.main:app --reload  # Run API server

# Testing
cd sdk && pytest                        # SDK tests
cd backend && pytest                    # Backend tests

# Database migrations
cd backend && alembic upgrade head      # Run migrations
cd backend && alembic revision --autogenerate -m "description"  # New migration
```

## Architecture Decisions
- Multi-tenant via PostgreSQL schema separation (one schema per tenant)
- ClickHouse for high-volume prediction storage (append-only)
- SDK sends predictions async via background thread with local buffer
- All API endpoints versioned under `/api/v1/`
- Audit trail: append-only table, immutable logs

## NFR Targets (MVP)
- SDK decorator overhead: < 2ms p99
- Dashboard initial load: < 3s
- API supports 10K predictions/sec per tenant
- Code coverage: >= 80%
- All data encrypted at rest (AES-256) and in transit (TLS 1.3)

## Requirements
Full requirements document: `/home/andresqb/Documents/meridian-requirements.pdf`
