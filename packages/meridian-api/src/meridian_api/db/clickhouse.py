"""ClickHouse client — prediction storage."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import clickhouse_connect

if TYPE_CHECKING:
    from clickhouse_connect.driver import Client

    from meridian_api.api.v1.predictions import PredictionEvent
    from meridian_api.core.config import Settings

# Placeholder until auth (US-027) is wired.
PLACEHOLDER_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")

_TABLE = "meridian.predictions"
_COLUMNS = [
    "prediction_id",
    "tenant_id",
    "model_name",
    "model_version",
    "timestamp",
    "latency_ms",
    "inputs",
    "output",
    "confidence",
    "risk_level",
]


def create_ch_client(settings: Settings) -> Client:
    """Create a ClickHouse client from application settings."""
    return clickhouse_connect.get_client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_port,
        database=settings.clickhouse_database,
    )


def _event_to_row(event: PredictionEvent) -> list:
    """Map a PredictionEvent to a ClickHouse row (column-ordered)."""
    return [
        uuid.UUID(event.prediction_id),
        PLACEHOLDER_TENANT_ID,
        event.model_name,
        "",  # model_version — not in PredictionEvent yet
        datetime.fromtimestamp(event.timestamp, tz=UTC),
        event.latency_ms,
        json.dumps(event.inputs),
        json.dumps(event.output),
        None,  # confidence
        None,  # risk_level
    ]


def insert_predictions(client: Client, predictions: list[PredictionEvent]) -> int:
    """Insert predictions into ClickHouse. Returns number of rows inserted."""
    rows = [_event_to_row(p) for p in predictions]
    client.insert(_TABLE, rows, column_names=_COLUMNS)
    return len(rows)
