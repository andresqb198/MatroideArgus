-- ClickHouse schema for prediction storage (E2 · Observabilidad)
-- Optimized for high-volume append-only writes and time-range queries

CREATE DATABASE IF NOT EXISTS meridian;

CREATE TABLE IF NOT EXISTS meridian.predictions
(
    prediction_id   UUID,
    tenant_id       UUID,
    model_name      LowCardinality(String),
    model_version   String DEFAULT '',
    timestamp       DateTime64(3, 'UTC'),
    latency_ms      Float32,
    inputs          String,           -- JSON serialized
    output          String,           -- JSON serialized
    confidence      Nullable(Float32),
    risk_level      LowCardinality(Nullable(String)),  -- HIGH/MED/LOW
    created_at      DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (tenant_id, model_name, timestamp)
TTL toDateTime(timestamp) + INTERVAL 2 YEAR
SETTINGS index_granularity = 8192;
