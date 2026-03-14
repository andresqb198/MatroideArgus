"""Meridian client — manages connection, configuration, and prediction shipping."""

from __future__ import annotations

import threading
from typing import Any

from meridian_sdk.buffer import PredictionBuffer
from meridian_sdk.config import MeridianConfig


class MeridianClient:
    """Central client for the Meridian SDK.

    Manages configuration, background shipping of predictions,
    and connection health to the Meridian backend.
    """

    _instance: MeridianClient | None = None
    _lock = threading.Lock()

    def __init__(self, config: MeridianConfig | None = None) -> None:
        self._config = config or MeridianConfig.from_env()
        self._config.validate()
        self._buffer = PredictionBuffer(
            flush_interval=self._config.flush_interval,
            api_url=self._config.api_url,
            api_key=self._config.api_key,
        )
        self._buffer.start()

    @classmethod
    def get_instance(cls) -> MeridianClient:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def init(cls, **kwargs: Any) -> MeridianClient:
        """Initialize the global Meridian client."""
        config = MeridianConfig(**kwargs)
        with cls._lock:
            cls._instance = cls(config=config)
        return cls._instance

    def log_prediction(self, prediction: dict[str, Any]) -> None:
        """Add a prediction to the local buffer for async shipping."""
        self._buffer.add(prediction)

    def shutdown(self) -> None:
        """Flush remaining predictions and stop the background thread."""
        self._buffer.stop()

    @property
    def config(self) -> MeridianConfig:
        return self._config
