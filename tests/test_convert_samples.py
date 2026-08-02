"""Convert every colab sample to every valid output for its input format."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tests.convert_coverage import SERVICES, list_samples, run  # noqa: E402


def test_convert_samples(*, max_jobs: int | None = None) -> list[str]:
    failures: list[str] = []
    missing = [s for s in SERVICES if not list_samples(s)]
    if missing:
        failures.append(f"no samples for services: {missing}")

    report = run(inventory_only=False, max_jobs=max_jobs)
    conv = report.get("convert") or {}
    if int(conv.get("total") or 0) <= 0:
        failures.append("no convert jobs planned — add files under colab/*/samples/")
    for job in conv.get("jobs") or []:
        if not job.get("ok"):
            failures.append(
                f"{job.get('service')} {job.get('file')} "
                f"({job.get('input_format')}→{job.get('output_format')}): {job.get('detail')}"
            )

    inv = report.get("totals") or {}
    print(
        f"Advertised routes: {inv.get('routes')} | "
        f"jobs: {conv.get('total')} | "
        f"covered pairs: {conv.get('covered_pairs')} | "
        f"PASS {conv.get('pass')} / FAIL {conv.get('fail')}"
    )
    return failures


if __name__ == "__main__":
    # Optional cap for quick local loops: CONVERT_MAX_JOBS=20
    import os

    raw = os.environ.get("CONVERT_MAX_JOBS", "").strip()
    max_jobs = int(raw) if raw.isdigit() else None
    fails = test_convert_samples(max_jobs=max_jobs)
    if fails:
        print(f"FAIL {len(fails)} convert job(s)")
        for f in fails[:50]:
            print(" -", f)
        if len(fails) > 50:
            print(f" - … {len(fails) - 50} more")
        sys.exit(1)
    print("PASS convert samples × all outputs")
