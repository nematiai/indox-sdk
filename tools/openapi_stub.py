"""Fallback operation docs for allowlist ops neither source schema describes.

A stub is a gate failure, not a feature: every stub carries
``x-indox-schema-source: synthesized`` so check_drift.py can refuse it.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from allowlist import AllowlistOp  # noqa: E402
from openapi_sources import SOURCE_SYNTHESIZED, operation_id, path_params  # noqa: E402

BLOCKED = (
    "/api/v1/business/",
    "/api/v1/audit/",
    "/api/v1/oidc/",
    "/api/v1/social/",
    "/api/v1/subscription/admin/",
    "/email-template/",
    "/selftest",
)


def is_blocked(path: str) -> bool:
    return any(b in path for b in BLOCKED)


def tag_for(path: str) -> str:
    segs = [s for s in path.strip("/").split("/") if s and not s.startswith("{")]
    if len(segs) >= 3 and segs[0] == "api" and segs[1] == "v1":
        if segs[2] == "convert" and len(segs) >= 4:
            return f"convert_{segs[3]}"
        return segs[2]
    return "indox"


def stub_operation(op: AllowlistOp) -> dict[str, Any]:
    doc: dict[str, Any] = {
        "operationId": operation_id(op.method, op.path),
        "summary": f"{op.method} {op.path}",
        "tags": [tag_for(op.path)],
        "x-indox-sdk-tier": op.tier.lower(),
        "x-indox-schema-source": SOURCE_SYNTHESIZED,
        "security": [{"ApiKeyBearer": []}],
        "responses": {
            "200": {"description": "OK"},
            "202": {"description": "Accepted"},
            "400": {"description": "Bad request"},
            "401": {"description": "Unauthorized"},
            "404": {"description": "Not found"},
        },
    }
    params = path_params(op.path)
    if params:
        doc["parameters"] = params
    if op.method in {"POST", "PUT", "PATCH"}:
        doc["requestBody"] = {
            "required": False,
            "content": {
                "application/json": {"schema": {"type": "object", "additionalProperties": True}},
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {"file": {"type": "string", "format": "binary"}},
                    }
                },
            },
        }
    return doc
