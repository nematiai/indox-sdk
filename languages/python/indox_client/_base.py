"""Base HTTP client with shared logic."""

from __future__ import annotations

import json
from typing import Any, Mapping, Optional

import requests

from ._exceptions import APIConnectionError, raise_for_status
from ._transport import build_headers, build_url, is_same_origin
from ._version import __version__

__all__ = ["BaseClient", "DEFAULT_TIMEOUT"]

DEFAULT_TIMEOUT = (5.0, 60.0)  # (connect, read)


def _error_message(payload: dict[str, Any]) -> str:
    """The API reports failures under several keys; pick whichever is present.

    Reading only `detail` left the real reason buried in `.response` while the
    exception stringified to a bare "HTTP 404".
    """
    for key in ("detail", "error", "message", "non_field_errors"):
        value = payload.get(key)
        if isinstance(value, (list, tuple)):
            value = "; ".join(str(v) for v in value)
        if value:
            return str(value)
    return ""


class BaseClient:
    """Low-level HTTP client used by all resources."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: Optional[tuple[float, float]] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout or DEFAULT_TIMEOUT
        self._session = session or requests.Session()
        self._user_agent = f"indox-client/{__version__}"

    @property
    def base_url(self) -> str:
        return self._base_url

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
        data: Optional[Mapping[str, Any]] = None,
        files: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[tuple[float, float]] = None,
        stream: bool = False,
    ) -> Any:
        """Execute HTTP request and handle response."""
        url = build_url(self._base_url, path)
        final_headers = build_headers(
            user_agent=self._user_agent,
            api_key=self._api_key,
            send_auth=is_same_origin(self._base_url, url),
            extra=headers,
        )

        try:
            response = self._session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json_body,
                data=data,
                files=files,
                headers=final_headers,
                timeout=timeout or self._timeout,
                stream=stream,
            )
        except requests.RequestException as exc:
            raise APIConnectionError(f"Connection error: {exc}") from exc

        return self._handle_response(response, stream=stream)

    def _handle_response(self, response: requests.Response, stream: bool = False) -> Any:
        """Process response and raise appropriate errors."""
        if response.status_code >= 400:
            payload = self._safe_json(response)
            message = _error_message(payload) if isinstance(payload, dict) else response.text
            raise_for_status(
                response.status_code,
                message or f"HTTP {response.status_code}",
                response=payload if isinstance(payload, dict) else None,
                request_id=response.headers.get("X-Request-ID"),
            )

        if stream:
            return response

        if not response.content:
            return {}

        return self._safe_json(response)

    def _safe_json(self, response: requests.Response) -> Any:
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"raw": response.text}

    def get(self, path: str, **kwargs: Any) -> Any:
        return self.request("GET", path, **kwargs)

    def post(
        self,
        path: str,
        *,
        json_body: Optional[Mapping[str, Any]] = None,
        data: Optional[Mapping[str, Any]] = None,
        files: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        return self.request("POST", path, json_body=json_body, data=data, files=files, **kwargs)

    def patch(
        self,
        path: str,
        *,
        json_body: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        return self.request("PATCH", path, json_body=json_body, **kwargs)

    def put(
        self,
        path: str,
        *,
        json_body: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        return self.request("PUT", path, json_body=json_body, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Any:
        return self.request("DELETE", path, **kwargs)

    def close(self) -> None:
        self._session.close()
