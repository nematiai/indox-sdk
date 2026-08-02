"""Assert live Indox convert inventory includes all 5 services and their routes."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tests.convert_coverage import SERVICES, fetch_inventory, run  # noqa: E402


def test_convert_inventory() -> list[str]:
    """Inventory-only: every service must advertise formats + routes."""
    failures: list[str] = []
    report = run(inventory_only=True)
    inv = report.get("inventory") or {}
    expected = set(SERVICES)
    got = set(inv)
    if got != expected:
        failures.append(f"services mismatch: expected {sorted(expected)}, got {sorted(got)}")

    totals = report.get("totals") or {}
    if int(totals.get("routes") or 0) <= 0:
        failures.append("total routes must be > 0")
    if int(totals.get("formats") or 0) <= 0:
        failures.append("total formats must be > 0")

    for service in sorted(SERVICES):
        meta = inv.get(service) or {}
        routes = meta.get("routes")
        formats = meta.get("formats")
        pairs = meta.get("route_pairs") or []
        print(
            f"  {service}: formats={formats} routes={routes} "
            f"pairs_listed={len(pairs)} inputs={meta.get('inputs')} outputs={meta.get('outputs')}"
        )
        if not routes:
            failures.append(f"{service}: missing routes count")
        if not formats:
            failures.append(f"{service}: missing formats count")
        if len(pairs) == 0:
            failures.append(f"{service}: route_pairs empty — cannot cover converts in tests")

    print(
        f"Inventory TOTAL formats={totals.get('formats')} routes={totals.get('routes')}"
    )
    return failures


if __name__ == "__main__":
    fails = test_convert_inventory()
    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        sys.exit(1)
    print("PASS convert inventory")
