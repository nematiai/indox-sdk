"""3D model convert resource: client.models (canonical /api/v1/convert/model/)."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Optional

from .._paths import MODEL_PREFIX
from ._helpers import as_dict, require_path, wait_status

if TYPE_CHECKING:
    from .._client import Indox


class Models:
    def __init__(self, client: "Indox") -> None:
        self._client = client

    def formats(self) -> dict[str, Any]:
        return as_dict(self._client._http.get(f"{MODEL_PREFIX}/formats/"))

    def operations(self) -> dict[str, Any]:
        return as_dict(self._client._http.get(f"{MODEL_PREFIX}/operations/"))

    def convert(
        self,
        file_path: Optional[str | os.PathLike[str]] = None,
        *,
        target_format: Optional[str] = None,
        file_url: Optional[str] = None,
        s3_key: Optional[str] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        form = dict(data or {})
        if target_format:
            form["target_formats"] = target_format
        if file_url:
            form["file_url"] = file_url
        if s3_key:
            form["s3_key"] = s3_key
        if file_path is not None:
            path = require_path(file_path)
            with path.open("rb") as fh:
                return as_dict(
                    self._client._http.post(
                        f"{MODEL_PREFIX}/convert/",
                        data=form,
                        files={"file": (path.name, fh)},
                    )
                )
        return as_dict(
            self._client._http.post(f"{MODEL_PREFIX}/convert/", data=form)
        )

    def get(self, conversion_id: str) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{MODEL_PREFIX}/conversion/{conversion_id}/")
        )

    def wait(
        self,
        conversion_id: str,
        *,
        timeout: float = 180.0,
        poll_interval: float = 0.5,
    ) -> dict[str, Any]:
        return wait_status(self.get, conversion_id, timeout=timeout, poll_interval=poll_interval)

    def convert_and_wait(
        self,
        file_path: str | os.PathLike[str],
        *,
        target_format: str,
        timeout: float = 180.0,
        poll_interval: float = 0.5,
        data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        job = self.convert(file_path, target_format=target_format, data=data)
        cid = str(job.get("id") or job.get("conversion_id") or "")
        if not cid:
            raise ValueError(f"convert response missing id: {job!r}")
        return self.wait(cid, timeout=timeout, poll_interval=poll_interval)
