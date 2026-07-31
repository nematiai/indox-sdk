"""User resource (P2 subset): client.user"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Optional

from .._paths import USER_PREFIX
from ._helpers import as_dict, require_path

if TYPE_CHECKING:
    from .._client import Indox


class User:
    def __init__(self, client: "Indox") -> None:
        self._client = client

    def login(self, *, email: str, password: str, remember_me: bool = True) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{USER_PREFIX}/auth/login/",
                json_body={
                    "email": email,
                    "password": password,
                    "remember_me": remember_me,
                },
            )
        )

    def logout(self) -> dict[str, Any]:
        return as_dict(self._client._http.post(f"{USER_PREFIX}/auth/logout/", json_body={}))

    def me(self) -> dict[str, Any]:
        return as_dict(self._client._http.get(f"{USER_PREFIX}/me/"))

    def update_me(self, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(self._client._http.patch(f"{USER_PREFIX}/me/", json_body=payload))

    def list_files(self, **params: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{USER_PREFIX}/storage/files/", params=params or None)
        )

    def upload_file(self, file_path: str | os.PathLike[str], **data: Any) -> dict[str, Any]:
        path = require_path(file_path)
        with path.open("rb") as fh:
            return as_dict(
                self._client._http.post(
                    f"{USER_PREFIX}/storage/files/upload/",
                    data=data or {},
                    files={"file": (path.name, fh)},
                )
            )

    def register_file(self, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{USER_PREFIX}/storage/files/register/",
                json_body=payload,
            )
        )

    def download_files(self, payload: dict[str, Any]) -> Any:
        return self._client._http.post(
            f"{USER_PREFIX}/storage/files/download/",
            json_body=payload,
            stream=True,
        )

    def download_zip(self, payload: dict[str, Any]) -> Any:
        return self._client._http.post(
            f"{USER_PREFIX}/storage/files/download/zip/",
            json_body=payload,
            stream=True,
        )

    def delete_files(self, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{USER_PREFIX}/storage/files/delete/",
                json_body=payload,
            )
        )

    def usage(self, **params: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{USER_PREFIX}/usage/", params=params or None)
        )

    def usage_summary(self, **params: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{USER_PREFIX}/usage/summary/", params=params or None)
        )

    def usage_trend(self, **params: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{USER_PREFIX}/usage/trend/", params=params or None)
        )

    def recent_conversions(self, **params: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(
                f"{USER_PREFIX}/usage/recent-conversions/",
                params=params or None,
            )
        )

    def conversion_usage(self, conversion_id: str) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(
                f"{USER_PREFIX}/usage/conversions/{conversion_id}/"
            )
        )

    def list_shares(self, **params: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{USER_PREFIX}/shares/", params=params or None)
        )

    def create_share(self, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(f"{USER_PREFIX}/shares/", json_body=payload)
        )

    def delete_share(self, link_id: str) -> dict[str, Any]:
        return as_dict(self._client._http.delete(f"{USER_PREFIX}/shares/{link_id}/"))

    def public_share(self, token: str) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{USER_PREFIX}/shares/public/{token}/")
        )

    def public_share_download(self, token: str, payload: Optional[dict[str, Any]] = None) -> Any:
        return self._client._http.post(
            f"{USER_PREFIX}/shares/public/{token}/download/",
            json_body=payload or {},
            stream=True,
        )
