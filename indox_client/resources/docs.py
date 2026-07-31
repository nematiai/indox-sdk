"""Docs core resource: client.docs"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

from .._paths import DOCS_PREFIX
from ._helpers import as_dict, wait_or_fallback, wait_status

if TYPE_CHECKING:
    from .._client import Indox


class Docs:
    def __init__(self, client: "Indox") -> None:
        self._client = client

    def credits(self) -> dict[str, Any]:
        return as_dict(self._client._http.get(f"{DOCS_PREFIX}/credits/"))

    def get(self, conversion_id: str) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{DOCS_PREFIX}/conversion/{conversion_id}/")
        )

    def wait(
        self,
        conversion_id: str,
        *,
        timeout: float = 180.0,
        poll_interval: float = 0.5,
    ) -> dict[str, Any]:
        def _get(cid: str) -> dict[str, Any]:
            return wait_or_fallback(
                lambda: as_dict(
                    self._client._http.get(f"{DOCS_PREFIX}/conversion/wait/{cid}/")
                ),
                lambda: self.get(cid),
            )

        return wait_status(_get, conversion_id, timeout=timeout, poll_interval=poll_interval)

    def batch_collect(self, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(f"{DOCS_PREFIX}/batch/collect/", json_body=payload)
        )

    def batch_download(
        self,
        batch_id: str,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Any:
        response = self._client._http.get(
            f"{DOCS_PREFIX}/batch/{batch_id}/download/",
            stream=True,
        )
        if output_path is None:
            return response
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)
        return target

    def hide(self, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(f"{DOCS_PREFIX}/visibility/hide/", json_body=payload)
        )
