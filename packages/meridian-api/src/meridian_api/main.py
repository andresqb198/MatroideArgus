"""Meridian Backend — FastAPI application entry point."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from meridian_api.api.v1 import router as api_v1_router
from meridian_api.core.config import settings
from meridian_api.db.clickhouse import create_ch_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Manage application startup/shutdown resources."""
    ch_client = create_ch_client(settings)
    logger.info("ClickHouse client connected to %s:%s", settings.clickhouse_host, settings.clickhouse_port)
    app.state.ch_client = ch_client
    yield
    ch_client.close()
    logger.info("ClickHouse client closed")


app = FastAPI(
    title="Meridian API",
    description="AI Ops & Governance Platform API",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "version": "0.1.0"}
