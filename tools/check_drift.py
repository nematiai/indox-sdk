"""Gate openapi-public.json against the ALLOWLIST *and* against the source schemas.

Three checks, because presence alone is tautological — build_openapi_public.py
writes a path item for every allowlist op, so a "missing" op cannot occur:

  1. presence   — every allowlist op has a path item          (regression guard)
  2. provenance — zero ops came from a synthesized stub       (the real content gate)
  3. sources    — every allowlist op resolves in the live schema or the DRF dump
                  (the only check that can see a deleted/renamed endpoint)

Check 3 needs the running stack. It is skipped only with an explicit --offline, which
exits 3 (UNVERIFIED) so no CI can read it as a pass; an unreachable stack without that
flag is a FAIL. Known limit, reported on every run: ops that resolve ONLY in the
checked-in DRF dump are verified against a file this gate never refreshes.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from allowlist import v1_ops  # noqa: E402
from drift_checks import check_presence, check_provenance, check_sources  # noqa: E402
from openapi_sources import (  # noqa: E402
    DRF_OUT,
    PUBLIC_OUT,
    LiveSchemaUnavailable,
    dev_base_url,
)
from openapi_stub import is_blocked  # noqa: E402

MAX_SHOWN = 50
EXIT_UNVERIFIED = 3


def _report(title: str, rows: list[str]) -> None:
    print(f"DRIFT: {len(rows)} {title}")
    for row in rows[:MAX_SHOWN]:
        print(" ", row)
    if len(rows) > MAX_SHOWN:
        print(f"  … +{len(rows) - MAX_SHOWN} more")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=PUBLIC_OUT)
    parser.add_argument("--drf", type=Path, default=DRF_OUT)
    parser.add_argument("--base-url", default=None)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip the source check (checks 1-2 only) — never use as a CI gate",
    )
    args = parser.parse_args()
    if not args.schema.is_file():
        raise SystemExit(f"Missing schema: {args.schema}")

    data = json.loads(args.schema.read_text(encoding="utf-8"))
    paths = data.get("paths") or {}
    ops = [op for op in v1_ops(include_adv=True) if not is_blocked(op.path)]

    for title, rows in (
        ("allowlist ops missing from the public schema", check_presence(paths)),
        ("ops are synthesized stubs, not real schema", check_provenance(paths)),
    ):
        if rows:
            _report(title, rows)
            raise SystemExit(1)

    counter = data.get("x-indox-synthesized-ops")
    if counter:
        print(f"DRIFT: x-indox-synthesized-ops={counter} (expected 0)")
        raise SystemExit(1)

    if args.offline:
        # Exit 3, not 0: a CI reading only the exit code must not mistake a partial
        # run for a full pass.
        print(f"PARTIAL drift check (OFFLINE — sources unverified): {len(ops)} ops in {args.schema}")
        raise SystemExit(EXIT_UNVERIFIED)

    # Never servers[0].url — that is the PUBLIC url the clients ship with; probing
    # it would point this gate at production.
    base_url = (args.base_url or dev_base_url()).rstrip("/")
    try:
        stale, drf_only = check_sources(base_url, args.drf)
    except LiveSchemaUnavailable as exc:
        print(f"DRIFT: live schema unreachable, cannot verify sources — {exc}")
        raise SystemExit(1) from exc
    if stale:
        _report(f"allowlist ops absent from the live/DRF sources at {base_url}", stale)
        raise SystemExit(1)

    print(
        f"OK drift check: {len(ops)} allowlist ops present, 0 stubs, "
        f"{len(ops) - drf_only} resolved live at {base_url}"
    )
    if drf_only:
        dumped = datetime.fromtimestamp(args.drf.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print(
            f"  NOTE {drf_only} op(s) resolved only via {args.drf.name} (dumped {dumped}), "
            "not against the running stack — re-run `make openapi-drf` to refresh it."
        )


if __name__ == "__main__":
    main()
