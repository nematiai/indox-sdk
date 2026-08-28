"""Source schemas for the public SDK spec — the live ninja schema + the DRF dump.

Shared by build_openapi_public.py (merge) and check_drift.py (gate), so the gate
resolves allowlist ops against the *sources* rather than against the file the
builder derived from the same allowlist.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from env import require_env  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
FEATURE = REPO / "spec"
PUBLIC_OUT = FEATURE / "openapi-public.json"
DRF_OUT = FEATURE / "openapi-drf.json"


def dev_base_url() -> str:
    """Where the tools READ the live schema from — a developer stack."""
    return require_env("INDOX_BASE_URL").rstrip("/")


def public_api_url() -> str:
    """What the spec PUBLISHES as servers[0].url — baked into every generated client."""
    return require_env("INDOX_PUBLIC_BASE_URL").rstrip("/")

SOURCE_LIVE = "live"
SOURCE_DRF = "drf-spectacular"
SOURCE_SYNTHESIZED = "synthesized"

_PARAM_RE = re.compile(r"\{([^}/]+)\}")


class LiveSchemaUnavailable(RuntimeError):
    """The running stack could not serve /api/v1/openapi.json."""


def fetch_live(base_url: str, *, timeout: int = 60) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/api/v1/openapi.json"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError) as exc:
        raise LiveSchemaUnavailable(f"{url}: {exc}") from exc


def load_drf(path: Path | None = None) -> dict[str, Any]:
    p = path or DRF_OUT
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def norm_path(path: str) -> str:
    path = path.strip()
    if not path.startswith("/"):
        path = "/" + path
    if "{" not in path.rstrip("/").split("/")[-1] and not path.endswith("/"):
        path = path + "/"
    return path


def index_paths(paths: dict[str, Any] | None) -> dict[str, Any]:
    return {norm_path(k): v for k, v in (paths or {}).items()}


def operation_id(method: str, path: str) -> str:
    cleaned: list[str] = []
    for part in (p for p in path.strip("/").split("/") if p):
        if part.startswith("{") and part.endswith("}"):
            cleaned.append("by_" + part[1:-1].replace("-", "_"))
        else:
            cleaned.append(part.replace("-", "_"))
    return method.lower() + "_" + "_".join(cleaned)


def path_params(path: str) -> list[dict[str, Any]]:
    return [
        {"name": name, "in": "path", "required": True, "schema": {"type": "string"}}
        for name in _PARAM_RE.findall(path)
    ]


def lookup_op(path: str, method: str, *path_maps: dict[str, Any]) -> dict[str, Any] | None:
    method_key = method.lower()
    alt = path.rstrip("/") or "/"
    for paths in path_maps:
        for candidate in (path, alt, alt + "/"):
            op = (paths.get(candidate) or {}).get(method_key)
            if op:
                return op
    return None


def _mark_upload_fields_binary(schemas: dict[str, Any], names: set[str]) -> int:
    """Give DRF upload fields the ``format: binary`` drf-spectacular does not emit.

    A ``serializers.FileField`` comes out of the DRF dump as a bare ``type: string``
    (verified: zero properties in openapi-drf.json carry ``format: binary``), so
    openapi-generator types every upload parameter as a string and the generated
    clients physically cannot send a file — the six convert endpoints are reachable
    only via ``file_url``/``s3_key``. Rust is the worst of them: it sends the string
    as a text form part, so the call looks like it succeeded.

    Applied only to schemas that came from the DRF dump, so the ninja half — where a
    property called ``file`` really is a URL string — is left alone.

    ponytail: patched here rather than in the backend because the backend shares one
    component between multipart/form-data and application/json, so it cannot carry
    ``binary`` without splitting the serializer in two. Restoring the deleted
    ``force_multipart_file_binary`` hook (backend 65c15fb) would fix the Scalar UI too;
    do that as well, not instead — this patch survives any dump refresh.
    """
    patched = 0
    for name in names:
        props = (schemas.get(name) or {}).get("properties")
        if not isinstance(props, dict):
            continue
        for key in ("file", "files"):
            prop = props.get(key)
            if not isinstance(prop, dict) or prop.get("format"):
                continue
            target = prop.setdefault("items", {}) if prop.get("type") == "array" else prop
            if target.get("type") in (None, "string"):
                target["type"] = "string"
                target["format"] = "binary"
                patched += 1
    return patched


def merge_components(live: dict[str, Any], drf: dict[str, Any]) -> dict[str, Any]:
    components = dict(live.get("components") or {})
    for section, blob in dict(drf.get("components") or {}).items():
        if not isinstance(blob, dict):
            continue
        target = dict(components.get(section) or {})
        for k, v in blob.items():
            target.setdefault(k, v)
        components[section] = target
    drf_schema_names = set((drf.get("components") or {}).get("schemas") or {})
    _mark_upload_fields_binary(components.get("schemas") or {}, drf_schema_names)
    schemes = dict(components.get("securitySchemes") or {})
    schemes["ApiKeyBearer"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "API key",
        "description": "Authorization: Bearer ak_…",
    }
    components["securitySchemes"] = schemes
    return components
