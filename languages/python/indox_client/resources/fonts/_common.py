"""Shared internals for the fonts resource."""

from __future__ import annotations

import os
from typing import Any, Optional, cast

from .._helpers import require_path


def normalize_format(fmt: str) -> str:
    """Normalize format string: lowercase, no leading dot."""
    return (fmt or "").strip().lower().lstrip(".")


def post_font_file(
    http: Any,
    endpoint: str,
    file_path: str | os.PathLike[str],
    *,
    params: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """POST a local font file as multipart form data."""
    path = require_path(file_path)
    with path.open("rb") as fh:
        return cast(
            dict[str, Any],
            http.post(endpoint, data={}, files={"file": (path.name, fh)}, params=params),
        )
