"""Meridian Backend — FastAPI application entry point."""

from fastapi import FastAPI

from app.api.v1 import router as api_v1_router
from app.core.config import settings

app = FastAPI(
    title="Meridian API",
    description="AI Ops & Governance Platform API",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/api/v1/openapi.json",
)

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "version": "0.1.0"}
