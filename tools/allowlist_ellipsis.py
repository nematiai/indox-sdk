"""Concrete paths behind the abbreviated (…) ADV rows in ALLOWLIST.md.

Kept beside the parser rather than inside it: an unrecognised abbreviated row is
fatal, so this table is the single place to extend when a new ADV group appears.
"""
from __future__ import annotations

from pathlib import Path

from allowlist_types import AllowlistOp

_ELLIPSIS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {
    "pipeline": (
        ("GET", "/api/v1/pdf_handler/pipeline/"),
        ("POST", "/api/v1/pdf_handler/pipeline/"),
        ("GET", "/api/v1/pdf_handler/pipeline/{pipeline_id}/"),
        ("DELETE", "/api/v1/pdf_handler/pipeline/{pipeline_id}/"),
        ("POST", "/api/v1/pdf_handler/pipeline/{pipeline_id}/run/"),
    ),
    "scan": (
        ("POST", "/api/v1/pdf_handler/scan/sessions/"),
        ("GET", "/api/v1/pdf_handler/scan/sessions/{session_id}/"),
        ("POST", "/api/v1/pdf_handler/scan/sessions/{session_id}/finalize/"),
        ("GET", "/api/v1/pdf_handler/scan/pair/"),
        ("POST", "/api/v1/pdf_handler/scan/pair/pages/"),
        ("DELETE", "/api/v1/pdf_handler/scan/pair/pages/{page_id}/"),
    ),
    "signing": (
        ("POST", "/api/v1/pdf_handler/signing/sessions/"),
        ("GET", "/api/v1/pdf_handler/signing/sessions/{session_id}/"),
        ("GET", "/api/v1/pdf_handler/signing/sign/{token}/"),
        ("POST", "/api/v1/pdf_handler/signing/sign/{token}/"),
        ("POST", "/api/v1/pdf_handler/signing/sign/{token}/decline/"),
        # Added by backend a88475f (signer certs). Missing here meant the allowlist
        # under-expanded silently — an under-populated group raises nothing, and
        # check_presence only walks allowlist -> spec, so no gate could see it.
        ("POST", "/api/v1/pdf_handler/signing/sign/{token}/certificate/"),
        ("POST", "/api/v1/pdf_handler/signing/sign/{token}/wet-signature/"),
    ),
}


def _expand_ellipsis(op: AllowlistOp) -> list[AllowlistOp]:
    """Map an abbreviated ADV row to its concrete public paths.

    An unrecognised row is fatal, never empty: silently dropping an op removes it
    from the allowlist, the generated spec AND the drift gate at once.
    """
    for marker, templates in _ELLIPSIS_GROUPS.items():
        if marker in op.path:
            return [
                AllowlistOp(method=m, path=p, tier=op.tier, raw_sdk=op.raw_sdk)
                for m, p in templates
            ]
    raise SystemExit(
        f"ALLOWLIST.md: abbreviated row {op.method} {op.path!r} matches no group in "
        f"_ELLIPSIS_GROUPS ({', '.join(_ELLIPSIS_GROUPS)}). Add its concrete paths to "
        f"{Path(__file__).name} — an unexpanded row would vanish from the allowlist silently."
    )
