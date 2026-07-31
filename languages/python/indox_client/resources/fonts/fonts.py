"""Fonts resource: client.fonts"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, cast

from ..._paths import FONTS_PREFIX
from .._helpers import require_response_key
from ._common import normalize_format, post_font_file
from .conversions import Conversions
from .formats import Formats

if TYPE_CHECKING:
    from ..._client import Indox


class Fonts:
    """
    Font conversion API.

    Sub-resources:
        - formats: List and query supported formats
        - conversions: Get status, wait, download

    Direct methods:
        - upload(): Upload font file to S3
        - convert(): Start conversion from S3 key
        - validate(): Validate conversion without executing
        - inspect(): Read font metadata without converting
        - quota(): Read caller quota (free IP or paid credits)

    Convenience methods:
        - convert_file(): Upload + convert in one call
        - convert_and_download(): Full pipeline
    """

    def __init__(self, client: "Indox") -> None:
        self._client = client
        self.formats = Formats(client)
        self.conversions = Conversions(client)

    def upload(self, file_path: str | os.PathLike[str]) -> dict[str, Any]:
        """Upload font file to object storage. Returns s3_key for convert()."""
        return post_font_file(self._client._http, f"{FONTS_PREFIX}/upload/", file_path)

    def convert(
        self,
        s3_key: str,
        *,
        target_format: str,
        filename: Optional[str] = None,
        external_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """Start conversion for an uploaded file."""
        fmt = normalize_format(target_format)
        if not fmt:
            raise ValueError("target_format is required")
        if not s3_key:
            raise ValueError("s3_key is required")

        payload: dict[str, Any] = {"s3_key": s3_key, "target_format": fmt}
        if filename:
            payload["filename"] = filename
        if external_token:
            payload["external_token"] = external_token

        return cast(
            dict[str, Any],
            self._client._http.post(f"{FONTS_PREFIX}/convert/", json_body=payload),
        )

    def validate(
        self,
        file_path: str | os.PathLike[str],
        *,
        target_format: Optional[str] = None,
    ) -> dict[str, Any]:
        """Validate conversion without executing."""
        params: dict[str, Any] = {}
        if target_format:
            params["target_format"] = normalize_format(target_format)

        return post_font_file(
            self._client._http,
            f"{FONTS_PREFIX}/validate/",
            file_path,
            params=params,
        )

    def inspect(self, file_path: str | os.PathLike[str]) -> dict[str, Any]:
        """Read font metadata from a local file (no conversion, no credit)."""
        return post_font_file(self._client._http, f"{FONTS_PREFIX}/inspect/", file_path)

    def inspect_by_key(self, s3_key: str) -> dict[str, Any]:
        """Read font metadata from an already-uploaded object key."""
        if not s3_key:
            raise ValueError("s3_key is required")
        return cast(
            dict[str, Any],
            self._client._http.get(f"{FONTS_PREFIX}/inspect/", params={"s3_key": s3_key}),
        )

    def quota(self) -> dict[str, Any]:
        """Read caller quota (free IP window or paid credits)."""
        return cast(dict[str, Any], self._client._http.get(f"{FONTS_PREFIX}/quota/"))

    def health(self) -> dict[str, Any]:
        """Fonts service health."""
        return cast(dict[str, Any], self._client._http.get(f"{FONTS_PREFIX}/health/"))

    def convert_file(
        self,
        file_path: str | os.PathLike[str],
        *,
        target_format: str,
        external_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """Upload and convert in one call."""
        upload_result = self.upload(file_path)
        return self.convert(
            require_response_key(upload_result, "s3_key", "Font upload"),
            target_format=target_format,
            filename=upload_result.get("filename"),
            external_token=external_token,
        )

    def convert_and_download(
        self,
        file_path: str | os.PathLike[str],
        *,
        target_format: str,
        output_path: str | Path,
        external_token: Optional[str] = None,
        timeout: float = 60.0,
        poll_interval: float = 0.5,
    ) -> Path:
        """Full pipeline: upload, convert, wait, download."""
        job = self.convert_file(
            file_path, target_format=target_format, external_token=external_token
        )
        job_id = require_response_key(job, "id", "Font conversion")
        self.conversions.wait(job_id, timeout=timeout, poll_interval=poll_interval)
        return self.conversions.download(job_id, output_path)
