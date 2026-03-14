"""Tests for the predictions batch endpoint."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from meridian_api.main import app

_BATCH_URL = "/api/v1/predictions/batch"
_PRED_ID_1 = "a0000000-0000-0000-0000-000000000001"
_PRED_ID_2 = "a0000000-0000-0000-0000-000000000002"
_SAMPLE_BATCH = {
    "predictions": [
        {
            "prediction_id": _PRED_ID_1,
            "model_name": "demo-model",
            "timestamp": 1710000000.0,
            "latency_ms": 1.5,
            "inputs": {"feature_a": 42},
            "output": "class_1",
        },
        {
            "prediction_id": _PRED_ID_2,
            "model_name": "demo-model",
            "timestamp": 1710000001.0,
            "latency_ms": 2.1,
            "inputs": {"feature_a": 7},
            "output": "class_0",
        },
    ]
}


# ── Unit tests (no ClickHouse needed) ──────────────────────────────────


@pytest.mark.asyncio
async def test_ingest_predictions_success():
    """POST /batch calls insert_predictions and returns 202 with accepted count."""
    mock_client = MagicMock()
    app.state.ch_client = mock_client

    with patch("meridian_api.api.v1.predictions.insert_predictions", return_value=2) as mock_insert:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(_BATCH_URL, json=_SAMPLE_BATCH)

    assert response.status_code == 202
    data = response.json()
    assert data["accepted"] == 2
    assert data["errors"] == 0

    mock_insert.assert_called_once()
    args = mock_insert.call_args
    assert args[0][0] is mock_client
    assert len(args[0][1]) == 2
    assert args[0][1][0].prediction_id == _PRED_ID_1


@pytest.mark.asyncio
async def test_ingest_predictions_clickhouse_error():
    """When insert_predictions raises, endpoint returns errors count."""
    mock_client = MagicMock()
    app.state.ch_client = mock_client

    with patch(
        "meridian_api.api.v1.predictions.insert_predictions",
        side_effect=RuntimeError("connection lost"),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(_BATCH_URL, json=_SAMPLE_BATCH)

    assert response.status_code == 202
    data = response.json()
    assert data["accepted"] == 0
    assert data["errors"] == 2


@pytest.mark.asyncio
async def test_ingest_predictions_empty_batch():
    """An empty batch is accepted with 0 counts."""
    mock_client = MagicMock()
    app.state.ch_client = mock_client

    with patch("meridian_api.api.v1.predictions.insert_predictions", return_value=0):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(_BATCH_URL, json={"predictions": []})

    assert response.status_code == 202
    data = response.json()
    assert data["accepted"] == 0
    assert data["errors"] == 0


# ── Integration tests (require running ClickHouse) ─────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ingest_predictions_integration():
    """End-to-end: POST batch → query ClickHouse → verify row landed."""
    import uuid

    from meridian_api.core.config import settings
    from meridian_api.db.clickhouse import create_ch_client

    # Use unique IDs per run so tests are idempotent.
    run_id_1 = str(uuid.uuid4())
    run_id_2 = str(uuid.uuid4())
    batch = {
        "predictions": [
            {**_SAMPLE_BATCH["predictions"][0], "prediction_id": run_id_1},
            {**_SAMPLE_BATCH["predictions"][1], "prediction_id": run_id_2},
        ]
    }

    ch_client = create_ch_client(settings)
    app.state.ch_client = ch_client

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(_BATCH_URL, json=batch)

        assert response.status_code == 202
        data = response.json()
        assert data["accepted"] == 2

        result = ch_client.query(
            "SELECT prediction_id, model_name, latency_ms "
            "FROM meridian.predictions "
            "WHERE prediction_id IN ({run_id_1:String}, {run_id_2:String})",
            parameters={"run_id_1": run_id_1, "run_id_2": run_id_2},
        )
        rows = result.result_rows
        assert len(rows) == 2
        model_names = {row[1] for row in rows}
        assert "demo-model" in model_names
    finally:
        # Clean up test data.
        ch_client.command(
            "ALTER TABLE meridian.predictions DELETE WHERE prediction_id IN ({run_id_1:String}, {run_id_2:String})",
            parameters={"run_id_1": run_id_1, "run_id_2": run_id_2},
        )
        ch_client.close()
