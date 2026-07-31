"""Main Indox client (API v1)."""

from __future__ import annotations

import os
from typing import Optional

from ._base import BaseClient
from .resources import (
    Billing,
    Docs,
    Fonts,
    Health,
    Images,
    Media,
    Models,
    PDF,
    User,
    Videos,
    Webhooks,
)

DEFAULT_BASE_URL = "https://indox.org"


class Indox:
    """
    Indox API v1 client (P0–P3 public surface).

    Resources:
        health, fonts, pdf, docs, media, images, videos, models,
        webhooks, user, billing
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[tuple[float, float]] = None,
    ) -> None:
        key = (api_key or os.getenv("INDOX_API_KEY") or "").strip()
        url = (
            base_url or os.getenv("INDOX_BASE_URL") or DEFAULT_BASE_URL
        ).strip().rstrip("/")

        self._http = BaseClient(base_url=url, api_key=key, timeout=timeout)
        self.health = Health(self)
        self.fonts = Fonts(self)
        self.pdf = PDF(self)
        self.docs = Docs(self)
        self.media = Media(self)
        self.images = Images(self)
        self.videos = Videos(self)
        self.models = Models(self)
        self.webhooks = Webhooks(self)
        self.user = User(self)
        self.billing = Billing(self)

    @property
    def base_url(self) -> str:
        return self._http.base_url

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "Indox":
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"Indox(base_url={self.base_url!r})"
