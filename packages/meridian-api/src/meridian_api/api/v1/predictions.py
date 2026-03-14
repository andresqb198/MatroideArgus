"""Predictions API — receives prediction logs from the SDK."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel

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


@router.post(
    "/batch",
    response_model=PredictionBatchResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def ingest_predictions(batch: PredictionBatchRequest) -> PredictionBatchResponse:
    """Ingest a batch of predictions from the SDK."""
    # TODO: Write to ClickHouse
    return PredictionBatchResponse(accepted=len(batch.predictions))
