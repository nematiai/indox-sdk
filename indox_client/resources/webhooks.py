"""Webhooks resource: client.webhooks"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from .._paths import WEBHOOKS_PREFIX
from ._helpers import as_dict

if TYPE_CHECKING:
    from .._client import Indox


class Webhooks:
    def __init__(self, client: "Indox") -> None:
        self._client = client

    def list(self, **params: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{WEBHOOKS_PREFIX}/", params=params or None)
        )

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(f"{WEBHOOKS_PREFIX}/", json_body=payload)
        )

    def get(self, webhook_id: str) -> dict[str, Any]:
        return as_dict(self._client._http.get(f"{WEBHOOKS_PREFIX}/{webhook_id}/"))

    def update(self, webhook_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.patch(
                f"{WEBHOOKS_PREFIX}/{webhook_id}/",
                json_body=payload,
            )
        )

    def delete(self, webhook_id: str) -> dict[str, Any]:
        return as_dict(self._client._http.delete(f"{WEBHOOKS_PREFIX}/{webhook_id}/"))

    def deliveries(self, webhook_id: str, **params: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(
                f"{WEBHOOKS_PREFIX}/{webhook_id}/deliveries/",
                params=params or None,
            )
        )

    def test(self, webhook_id: str, payload: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{WEBHOOKS_PREFIX}/{webhook_id}/test/",
                json_body=payload or {},
            )
        )
