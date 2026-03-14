"""Tests for the prediction buffer."""

import time

from meridian_sdk.buffer import PredictionBuffer


def test_buffer_add_and_flush():
    buf = PredictionBuffer(flush_interval=60, api_url="", api_key="")
    buf.add({"prediction_id": "1", "model_name": "test"})
    buf.add({"prediction_id": "2", "model_name": "test"})
    assert len(buf._buffer) == 2


def test_buffer_respects_max_size():
    buf = PredictionBuffer(flush_interval=60, max_size=5, api_url="", api_key="")
    for i in range(10):
        buf.add({"prediction_id": str(i)})
    assert len(buf._buffer) == 5


def test_buffer_start_stop():
    buf = PredictionBuffer(flush_interval=0.1, api_url="", api_key="")
    buf.start()
    buf.add({"prediction_id": "1"})
    time.sleep(0.3)
    buf.stop()
    # Buffer should be empty after stop (flushed)
    assert len(buf._buffer) == 0
