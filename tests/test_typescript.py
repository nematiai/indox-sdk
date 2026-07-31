"""TypeScript / JavaScript SDK tests."""
from __future__ import annotations

import os
import subprocess

from .common import REPO, base_url, load_api_key, run_lang, skip_native, toolchain


def _native() -> list[str]:
    node = toolchain("typescript", "node", cwd=str(REPO))
    if not node:
        return skip_native("typescript", "node not installed")
    smoke = REPO / "languages" / "typescript" / "smoke.mjs"
    print("[typescript] node smoke.mjs")
    env = os.environ.copy()
    env["INDOX_BASE_URL"] = base_url()
    # Every sibling forwards the key; without it smoke.mjs self-skips and scores PASS.
    env["INDOX_API_KEY"] = load_api_key()
    proc = subprocess.run(
        [*node, str(smoke)],
        cwd=str(REPO),
        env=env,
        check=False,
    )
    if proc.returncode != 0:
        return [f"typescript smoke.mjs exited {proc.returncode}"]
    return []


def test_typescript() -> list[str]:
    return run_lang("typescript", native=_native)


if __name__ == "__main__":
    raise SystemExit(1 if test_typescript() else 0)
