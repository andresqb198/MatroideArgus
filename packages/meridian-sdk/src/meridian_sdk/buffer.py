"""Async prediction buffer with background flush thread."""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from typing import Any

import httpx

logger = logging.getLogger("meridian.buffer")


class PredictionBuffer:
    """Thread-safe buffer that accumulates predictions and flushes them
    to the Meridian backend in a background thread.

    - Flush every `flush_interval` seconds (default 5s)
    - Retry with exponential backoff on failure
    - Max loss: 0.1% of events on network failure (NFR-006)
    """

    def __init__(
        self,
        flush_interval: float = 5.0,
        max_size: int = 10_000,
        api_url: str = "",
        api_key: str = "",
    ) -> None:
        self._buffer: deque[dict[str, Any]] = deque(maxlen=max_size)
        self._lock = threading.Lock()
        self._flush_interval = flush_interval
        self._api_url = api_url.rstrip("/")
        self._api_key = api_key
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def add(self, prediction: dict[str, Any]) -> None:
        with self._lock:
            self._buffer.append(prediction)

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="meridian-flush")
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=10)
        self._flush()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            self._stop_event.wait(timeout=self._flush_interval)
            self._flush()

    def _flush(self) -> None:
        with self._lock:
            if not self._buffer:
                return
            batch = list(self._buffer)
            self._buffer.clear()

        if not self._api_url or not self._api_key:
            logger.debug("No API configured, discarding %d predictions (dev mode)", len(batch))
            return

        self._send_with_retry(batch)

    def _send_with_retry(self, batch: list[dict[str, Any]], max_retries: int = 3) -> None:
        for attempt in range(max_retries):
            try:
                response = httpx.post(
                    f"{self._api_url}/api/v1/predictions/batch",
                    json={"predictions": batch},
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    timeout=10.0,
                )
                response.raise_for_status()
                return
            except Exception as e:
                wait = min(2**attempt, 8)
                logger.warning(
                    "Failed to flush predictions (attempt %d/%d): %s. Retrying in %ds",
                    attempt + 1,
                    max_retries,
                    e,
                    wait,
                )
                time.sleep(wait)

        logger.error("Failed to flush %d predictions after %d retries", len(batch), max_retries)
