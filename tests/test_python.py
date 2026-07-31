"""Python SDK tests — package layout + full allowlist smoke + HTTP probes."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from .common import REPO, run_lang, skip_native


def _native() -> list[str]:
    """Run the existing allowlist script when LIVE is enabled (default on)."""
    if os.environ.get("SDK_TEST_SKIP_PYTHON_ALLOWLIST", "").lower() in {"1", "true", "yes"}:
        return skip_native("python", "SDK_TEST_SKIP_PYTHON_ALLOWLIST set")
    script = REPO / "tests" / "allowlist_smoke.py"
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{REPO}{os.pathsep}{env.get('PYTHONPATH', '')}"
    print(f"[{'python'}] allowlist → {script.name}")
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO),
        env=env,
        check=False,
    )
    if proc.returncode != 0:
        return [f"python allowlist exited {proc.returncode}"]
    return []


def test_python() -> list[str]:
    return run_lang("python", native=_native)


if __name__ == "__main__":
    fails = test_python()
    raise SystemExit(1 if fails else 0)
