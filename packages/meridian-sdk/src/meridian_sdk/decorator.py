"""The @observe decorator — core instrumentation entry point."""

from __future__ import annotations

import functools
import time
import uuid
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def observe(func: F | None = None, *, model_name: str | None = None) -> Any:
    """Decorator that captures predictions from any ML model's predict method.

    Usage:
        @meridian.observe
        def predict(features):
            return model.predict(features)

        # or with options:
        @meridian.observe(model_name="credit-risk-v2")
        def predict(features):
            return model.predict(features)
    """

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            from meridian_sdk.client import MeridianClient

            prediction_id = str(uuid.uuid4())
            start_time = time.perf_counter()

            result = fn(*args, **kwargs)

            latency_ms = (time.perf_counter() - start_time) * 1000
            name = model_name or fn.__qualname__

            try:
                client = MeridianClient.get_instance()
                client.log_prediction(
                    {
                        "prediction_id": prediction_id,
                        "model_name": name,
                        "timestamp": time.time(),
                        "latency_ms": latency_ms,
                        "inputs": _safe_serialize(args, kwargs),
                        "output": _safe_serialize_output(result),
                    }
                )
            except Exception:
                # NFR-006: SDK must never affect inference
                pass

            return result

        return wrapper  # type: ignore[return-value]

    if func is not None:
        return decorator(func)
    return decorator


def _safe_serialize(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    """Best-effort serialization of prediction inputs."""
    try:
        import numpy as np

        serialized_args = []
        for arg in args:
            if isinstance(arg, np.ndarray):
                serialized_args.append({"shape": list(arg.shape), "dtype": str(arg.dtype)})
            else:
                serialized_args.append(repr(arg)[:500])
        return {"args": serialized_args, "kwargs": {k: repr(v)[:500] for k, v in kwargs.items()}}
    except Exception:
        return {}


def _safe_serialize_output(result: Any) -> Any:
    """Best-effort serialization of prediction output."""
    try:
        import numpy as np

        if isinstance(result, np.ndarray):
            return {"shape": list(result.shape), "dtype": str(result.dtype), "values": result.tolist()[:100]}
        return repr(result)[:1000]
    except Exception:
        return repr(result)[:1000]
