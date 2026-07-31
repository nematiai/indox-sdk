"""PDF advanced ops (pipeline / scan / signing) mixed into PDF."""

from __future__ import annotations

from typing import Any, Optional

from .._paths import PDF_PREFIX
from ._helpers import as_dict


class PDFAdvancedMixin:
    """ADV routes under ``/api/v1/pdf_handler/``."""

    _client: Any

    # --- pipeline ---
    def list_pipelines(self) -> dict[str, Any]:
        return as_dict(self._client._http.get(f"{PDF_PREFIX}/pipeline/"))

    def create_pipeline(self, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(f"{PDF_PREFIX}/pipeline/", json_body=payload)
        )

    def get_pipeline(self, pipeline_id: str) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{PDF_PREFIX}/pipeline/{pipeline_id}/")
        )

    def delete_pipeline(self, pipeline_id: str) -> dict[str, Any]:
        return as_dict(
            self._client._http.delete(f"{PDF_PREFIX}/pipeline/{pipeline_id}/")
        )

    def run_pipeline(self, pipeline_id: str, payload: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{PDF_PREFIX}/pipeline/{pipeline_id}/run/",
                json_body=payload or {},
            )
        )

    # --- scan sessions ---
    def create_scan_session(self, payload: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{PDF_PREFIX}/scan/sessions/",
                json_body=payload or {},
            )
        )

    def get_scan_session(self, session_id: str) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{PDF_PREFIX}/scan/sessions/{session_id}/")
        )

    def finalize_scan_session(self, session_id: str, payload: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{PDF_PREFIX}/scan/sessions/{session_id}/finalize/",
                json_body=payload or {},
            )
        )

    def get_scan_pair(self, **params: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{PDF_PREFIX}/scan/pair/", params=params or None)
        )

    def upload_scan_pair_page(self, payload: Optional[dict[str, Any]] = None, **kwargs: Any) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{PDF_PREFIX}/scan/pair/pages/",
                json_body=payload,
                **kwargs,
            )
        )

    def delete_scan_pair_page(self, page_id: str) -> dict[str, Any]:
        return as_dict(
            self._client._http.delete(f"{PDF_PREFIX}/scan/pair/pages/{page_id}/")
        )

    # --- signing ---
    def create_signing_session(self, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{PDF_PREFIX}/signing/sessions/",
                json_body=payload,
            )
        )

    def get_signing_session(self, session_id: str) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{PDF_PREFIX}/signing/sessions/{session_id}/")
        )

    def get_sign_token(self, token: str) -> dict[str, Any]:
        return as_dict(
            self._client._http.get(f"{PDF_PREFIX}/signing/sign/{token}/")
        )

    def submit_sign(self, token: str, payload: dict[str, Any]) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{PDF_PREFIX}/signing/sign/{token}/",
                json_body=payload,
            )
        )

    def decline_sign(self, token: str, payload: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return as_dict(
            self._client._http.post(
                f"{PDF_PREFIX}/signing/sign/{token}/decline/",
                json_body=payload or {},
            )
        )
