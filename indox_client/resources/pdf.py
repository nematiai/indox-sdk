"""PDF handler resource: client.pdf (P0 core + ADV)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from .._paths import PDF_PREFIX
from ._helpers import as_dict, require_path, wait_status
from .pdf_adv import PDFAdvancedMixin

if TYPE_CHECKING:
    from .._client import Indox


class PDF(PDFAdvancedMixin):
    """Document/PDF API under ``/api/v1/pdf_handler/``."""

    def __init__(self, client: "Indox") -> None:
        self._client = client

    def formats(self) -> dict[str, Any]:
        return as_dict(self._client._http.get(f"{PDF_PREFIX}/formats/"))

    def operations(self, **params: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{PDF_PREFIX}/operations/", params=params or None)
        )

    def history(self, **params: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{PDF_PREFIX}/history/", params=params or None)
        )

    def convert(
        self,
        file_path: str | os.PathLike[str],
        *,
        target_format: Optional[str] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        path = require_path(file_path)
        form = dict(data or {})
        if target_format:
            form["target_formats"] = target_format
        with path.open("rb") as fh:
            return as_dict(
                self._client._http.post(
                    f"{PDF_PREFIX}/convert/",
                    data=form,
                    files={"file": (path.name, fh)},
                )
            )

    def convert_json(self, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(f"{PDF_PREFIX}/convert/json/", json_body=payload)
        )

    def form_fields(self, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(f"{PDF_PREFIX}/form-fields/", json_body=payload)
        )

    def save(self, file_path: str | os.PathLike[str], **data: Any) -> dict[str, Any]:
        path = require_path(file_path)
        with path.open("rb") as fh:
            return as_dict(
                self._client._http.post(
                    f"{PDF_PREFIX}/save/",
                    data=data or {},
                    files={"file": (path.name, fh)},
                )
            )

    def get(self, conversion_id: str) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{PDF_PREFIX}/conversion/{conversion_id}/")
        )

    def wait(
        self,
        conversion_id: str,
        *,
        timeout: float = 180.0,
        poll_interval: float = 0.5,
    ) -> dict[str, Any]:
        return wait_status(
            self.get, conversion_id, timeout=timeout, poll_interval=poll_interval
        )

    def download(self, conversion_id: str, output_path: str | Path) -> Path:
        response = self._client._http.get(
            f"{PDF_PREFIX}/{conversion_id}/download/",
            stream=True,
        )
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)
        return target

    def convert_and_download(
        self,
        file_path: str | os.PathLike[str],
        *,
        target_format: str,
        output_path: str | Path,
        timeout: float = 180.0,
        poll_interval: float = 0.5,
        data: Optional[dict[str, Any]] = None,
    ) -> Path:
        job = self.convert(file_path, target_format=target_format, data=data)
        cid = str(job.get("id") or job.get("conversion_id") or "")
        if not cid:
            raise ValueError(f"convert response missing id: {job!r}")
        self.wait(cid, timeout=timeout, poll_interval=poll_interval)
        return self.download(cid, output_path)
