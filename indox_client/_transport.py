"""URL resolution and header preparation for the HTTP client."""

from __future__ import annotations

from typing import Mapping, Optional
from urllib.parse import urlsplit

ABSOLUTE_SCHEMES = ("http://", "https://")


def build_url(base_url: str, path: str) -> str:
    if path.startswith(ABSOLUTE_SCHEMES):
        return path
    suffix = path if path.startswith("/") else f"/{path}"
    return f"{base_url}{suffix}"


def is_same_origin(base_url: str, url: str) -> bool:
    base = urlsplit(base_url)
    target = urlsplit(url)
    if not base.netloc or not target.netloc:
        return False
    return (base.scheme.lower(), base.netloc.lower()) == (
        target.scheme.lower(),
        target.netloc.lower(),
    )


def build_headers(
    *,
    user_agent: str,
    api_key: str,
    send_auth: bool,
    extra: Optional[Mapping[str, str]] = None,
) -> dict[str, str]:
    headers = {
        "Accept": "application/json",
        "User-Agent": user_agent,
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if extra:
        headers.update({k: v for k, v in extra.items() if v is not None})
    if not send_auth:
        # A URL outside the configured origin must never carry the caller's credentials.
        for key in [k for k in headers if k.lower() == "authorization"]:
            headers.pop(key)
    return headers
