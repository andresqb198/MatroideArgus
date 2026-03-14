"""Configuration management for the Meridian SDK."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class MeridianConfig:
    """SDK configuration, loadable from environment variables or code."""

    api_key: str = ""
    api_url: str = "https://api.meridian.ai"
    project: str = ""
    env: str = "development"
    flush_interval: float = 5.0
    max_buffer_size: int = 10_000

    @classmethod
    def from_env(cls) -> MeridianConfig:
        """Load configuration from environment variables."""
        return cls(
            api_key=os.getenv("MERIDIAN_API_KEY", ""),
            api_url=os.getenv("MERIDIAN_API_URL", "https://api.meridian.ai"),
            project=os.getenv("MERIDIAN_PROJECT", ""),
            env=os.getenv("MERIDIAN_ENV", "development"),
        )

    def validate(self) -> None:
        """Validate that required configuration is present."""
        if not self.api_key and self.env != "development":
            raise ValueError(
                "MERIDIAN_API_KEY is required in non-development environments. "
                "Set it via environment variable or MeridianClient.init(api_key=...)"
            )
