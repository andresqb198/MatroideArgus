"""Tests for the @observe decorator."""

import time
from unittest.mock import patch

from meridian_sdk import observe


def test_observe_captures_return_value():
    @observe
    def predict(x: int) -> int:
        return x * 2

    assert predict(5) == 10


def test_observe_with_model_name():
    @observe(model_name="test-model")
    def predict(x: int) -> int:
        return x + 1

    assert predict(3) == 4


def test_observe_does_not_add_significant_latency():
    @observe
    def predict(x: int) -> int:
        return x

    start = time.perf_counter()
    for _ in range(1000):
        predict(1)
    elapsed_ms = (time.perf_counter() - start) * 1000

    # 1000 calls should complete well under 2 seconds (< 2ms overhead each)
    assert elapsed_ms < 2000


def test_observe_never_raises_on_client_error():
    """NFR-006: SDK must never affect inference."""

    with patch("meridian_sdk.client.MeridianClient.get_instance", side_effect=RuntimeError("boom")):

        @observe
        def predict(x: int) -> int:
            return x * 3

        # Should not raise despite client error
        assert predict(7) == 21
