"""Shared helpers for convert-style resources."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Callable, Optional, cast


WAIT_UNAVAILABLE_STATUSES = frozenset({404, 405})


def wait_or_fallback(
    fetch_wait: Callable[[], dict[str, Any]],
    fallback: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    """Poll the long-poll wait endpoint, falling back only when it is unavailable."""
    from .._exceptions import APIStatusError

    try:
        return fetch_wait()
    except APIStatusError as exc:
        if exc.status_code not in WAIT_UNAVAILABLE_STATUSES:
            raise
        return fallback()


def require_path(file_path: str | os.PathLike[str]) -> Path:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path


def require_response_key(payload: dict[str, Any], key: str, context: str) -> Any:
    from .._exceptions import ConversionError

    value = payload.get(key)
    if not value:
        raise ConversionError(
            f"{context} response is missing {key!r}; got keys: {sorted(payload)}"
        )
    return value


def wait_status(
    getter: Callable[[str], dict[str, Any]],
    conversion_id: str,
    *,
    timeout: float = 120.0,
    poll_interval: float = 0.5,
    done: str = "completed",
    failed: str = "failed",
) -> dict[str, Any]:
    from .._exceptions import ConversionError, ConversionTimeoutError

    start = time.time()
    while True:
        status = getter(conversion_id)
        state = str(status.get("status") or "").lower()
        if state == done or state == "success":
            return status
        if state == failed or state == "error":
            raise ConversionError(
                str(status.get("error") or status.get("detail") or "Conversion failed"),
                conversion_id=conversion_id,
            )
        if time.time() - start > timeout:
            raise ConversionTimeoutError(
                f"Conversion {conversion_id} timed out after {timeout}s"
            )
        time.sleep(poll_interval)


def as_dict(value: Any) -> dict[str, Any]:
    return cast(dict[str, Any], value)
