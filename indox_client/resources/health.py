"""Health resource: client.health"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from .._paths import HEALTH_PREFIX

if TYPE_CHECKING:
    from .._client import Indox


class Health:
    def __init__(self, client: "Indox") -> None:
        self._client = client

    def get(self) -> dict[str, Any]:
        return cast(dict[str, Any], self._client._http.get(f"{HEALTH_PREFIX}/"))
