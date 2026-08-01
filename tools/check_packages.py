"""Validate each <lang>/ tree is package-ready after codegen."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from openapi_sources import PUBLIC_OUT  # noqa: E402
from packages import REQUIRED  # noqa: E402

REPO = Path(__file__).resolve().parents[1]



def main() -> None:
    failures: list[str] = []
    for lang, rels in REQUIRED.items():
        for rel in rels:
            p = REPO / rel
            if not p.exists():
                failures.append(f"missing {rel}")
            else:
                print(f"  OK {rel}")
    if failures:
        print("FAIL package layout:")
        for f in failures:
            print(" ", f)
        if any("/generated" in f for f in failures):
            # generated/ is git-ignored — a fresh clone has none until codegen runs.
            # The spec IS tracked, so this needs Docker + network, not a running backend.
            print(
                f"\nRun `make gen-all` to build the generated clients first"
                f" (needs Docker + network; reads the tracked {PUBLIC_OUT.name},"
                f" so the backend does not have to be up)."
            )
            if not PUBLIC_OUT.is_file():
                print(f"Missing {PUBLIC_OUT} — run `make openapi` first (needs the stack up).")
        raise SystemExit(1)
    print(f"OK package layout for {len(REQUIRED)} languages")


if __name__ == "__main__":
    main()
