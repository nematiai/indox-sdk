"""Build spec/openapi-public.json from live schema + ALLOWLIST.

Missing DRF convert/media routes are filled from ``openapi-drf.json`` (spectacular)
when present, otherwise synthesized as stubs — which check_drift.py then rejects.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from allowlist import AllowlistOp, v1_ops  # noqa: E402
from openapi_sources import (  # noqa: E402
    DRF_OUT,
    PUBLIC_OUT,
    SOURCE_DRF,
    SOURCE_LIVE,
    dev_base_url,
    fetch_live,
    index_paths,
    load_drf,
    lookup_op,
    merge_components,
    operation_id,
    public_api_url,
)
from openapi_stub import is_blocked, stub_operation  # noqa: E402


def _adopt(source_op: dict[str, Any], op: AllowlistOp, source: str) -> dict[str, Any]:
    cloned = json.loads(json.dumps(source_op))
    cloned["operationId"] = cloned.get("operationId") or operation_id(op.method, op.path)
    cloned["x-indox-sdk-tier"] = op.tier.lower()
    cloned["x-indox-schema-source"] = source
    return cloned


def build(
    base_url: str,
    include_adv: bool = True,
    *,
    drf_schema: dict[str, Any] | None = None,
    live_schema: dict[str, Any] | None = None,
    public_url: str | None = None,
) -> dict[str, Any]:
    live = live_schema if live_schema is not None else fetch_live(base_url)
    live_paths = index_paths(dict(live.get("paths") or {}))
    drf = drf_schema if drf_schema is not None else load_drf()
    drf_paths = index_paths(dict(drf.get("paths") or {}))
    ops = v1_ops(include_adv=include_adv)

    public_paths: dict[str, Any] = {}
    synthesized = 0
    from_drf = 0

    for op in ops:
        if is_blocked(op.path):
            continue
        path_item = public_paths.setdefault(op.path, {})
        method_key = op.method.lower()
        found = lookup_op(op.path, op.method, live_paths)
        if found:
            path_item[method_key] = _adopt(found, op, SOURCE_LIVE)
            continue
        found = lookup_op(op.path, op.method, drf_paths)
        if found:
            path_item[method_key] = _adopt(found, op, SOURCE_DRF)
            from_drf += 1
            continue
        path_item[method_key] = stub_operation(op)
        synthesized += 1

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Indox API v1 (public SDK)",
            "version": "1.0.0",
            "description": (
                "Filtered public allowlist for official SDKs (P0–P3 + ADV). "
                "DRF converter routes merge from openapi-drf.json when available."
            ),
        },
        "servers": [{"url": (public_url or public_api_url()).rstrip("/")}],
        "paths": dict(sorted(public_paths.items())),
        "components": merge_components(live, drf),
        "security": [{"ApiKeyBearer": []}],
        "x-indox-allowlist-ops": len(ops),
        "x-indox-drf-ops": from_drf,
        "x-indox-synthesized-ops": synthesized,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=dev_base_url(),
        help="Where to READ the live schema from (a dev stack).",
    )
    parser.add_argument(
        "--public-url",
        default=public_api_url(),
        help="What to PUBLISH as servers[0].url — every generated client defaults to it.",
    )
    parser.add_argument("--out", type=Path, default=PUBLIC_OUT)
    parser.add_argument("--drf", type=Path, default=DRF_OUT)
    parser.add_argument("--no-adv", action="store_true")
    args = parser.parse_args()

    schema = build(
        args.base_url,
        include_adv=not args.no_adv,
        drf_schema=load_drf(args.drf),
        public_url=args.public_url,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(schema, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    n_ops = sum(
        len([k for k in v if k in {"get", "post", "put", "patch", "delete"}])
        for v in schema["paths"].values()
    )
    print(
        f"Wrote {args.out} paths={len(schema['paths'])} ops={n_ops} "
        f"drf={schema['x-indox-drf-ops']} synthesized={schema['x-indox-synthesized-ops']} "
        f"servers[0]={schema['servers'][0]['url']}"
    )


if __name__ == "__main__":
    main()
