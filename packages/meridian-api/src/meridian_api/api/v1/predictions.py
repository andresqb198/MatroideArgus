"""Predictions API — receives prediction logs from the SDK."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel

from meridian_api.db.clickhouse import insert_predictions

logger = logging.getLogger(__name__)

router = APIRouter()


class PredictionEvent(BaseModel):
    prediction_id: str
    model_name: str
    timestamp: float
    latency_ms: float
    inputs: dict[str, Any] = {}
    output: Any = None


class PredictionBatchRequest(BaseModel):
    predictions: list[PredictionEvent]


class PredictionBatchResponse(BaseModel):
    accepted: int
    errors: int = 0


def get_ch_client(request: Request):
    """Dependency: retrieve the ClickHouse client from app state."""
    return request.app.state.ch_client


@router.post(
    "/batch",
    response_model=PredictionBatchResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def ingest_predictions(
    batch: PredictionBatchRequest,
    ch_client=Depends(get_ch_client),  # noqa: B008
) -> PredictionBatchResponse:
    """Ingest a batch of predictions from the SDK."""
    try:
        inserted = await asyncio.to_thread(insert_predictions, ch_client, batch.predictions)
        return PredictionBatchResponse(accepted=inserted)
    except Exception:
        logger.exception("ClickHouse insert failed")
        return PredictionBatchResponse(accepted=0, errors=len(batch.predictions))
