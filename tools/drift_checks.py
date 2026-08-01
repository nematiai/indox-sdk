"""The three drift checks, separated from the CLI that reports them.

  presence   — every allowlist op has a path item          (regression guard)
  provenance — zero ops came from a synthesized stub       (the real content gate)
  sources    — every allowlist op resolves in the live schema or the DRF dump
               (the only check that can see a deleted/renamed endpoint)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from allowlist import v1_ops  # noqa: E402
from openapi_sources import (  # noqa: E402
    SOURCE_SYNTHESIZED,
    fetch_live,
    index_paths,
    load_drf,
    lookup_op,
)
from openapi_stub import is_blocked  # noqa: E402


def check_presence(paths: dict) -> list[str]:
    return [
        f"{op.method} {op.path}"
        for op in v1_ops(include_adv=True)
        if not is_blocked(op.path) and op.method.lower() not in (paths.get(op.path) or {})
    ]


def check_provenance(paths: dict) -> list[str]:
    rows: list[str] = []
    for path, item in paths.items():
        for method, doc in (item or {}).items():
            if isinstance(doc, dict) and doc.get("x-indox-schema-source") == SOURCE_SYNTHESIZED:
                rows.append(f"{method.upper()} {path} (stub — no live or DRF schema)")
    return sorted(rows)


def check_sources(base_url: str, drf_path: Path) -> tuple[list[str], int]:
    """Return (ops resolving nowhere, ops resolving ONLY in the checked-in DRF dump).

    The second number is the honest limit of this gate: those ops are verified
    against a file that `make ci` never refreshes, so deleting one of those routes
    in code would not be seen until `make openapi` re-dumps.
    """
    live_paths = index_paths(dict(fetch_live(base_url).get("paths") or {}))
    drf_paths = index_paths(dict(load_drf(drf_path).get("paths") or {}))
    stale: list[str] = []
    drf_only = 0
    for op in v1_ops(include_adv=True):
        if is_blocked(op.path):
            continue
        if lookup_op(op.path, op.method, live_paths) is not None:
            continue
        if lookup_op(op.path, op.method, drf_paths) is not None:
            drf_only += 1
            continue
        stale.append(f"{op.method} {op.path}")
    return stale, drf_only
