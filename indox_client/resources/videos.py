"""Video convert resource: client.videos (canonical /api/v1/convert/video/)."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Optional

from .._paths import VIDEO_PREFIX
from ._helpers import as_dict, require_path

if TYPE_CHECKING:
    from .._client import Indox


class Videos:
    def __init__(self, client: "Indox") -> None:
        self._client = client

    def formats(self) -> dict[str, Any]:
        return as_dict(self._client._http.get(f"{VIDEO_PREFIX}/formats/"))

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
                        f"{VIDEO_PREFIX}/convert/",
                        data=form,
                        files={"file": (path.name, fh)},
                    )
                )
        return as_dict(
            self._client._http.post(f"{VIDEO_PREFIX}/convert/", data=form)
        )
