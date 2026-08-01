"""TypeScript / JavaScript SDK tests."""
from __future__ import annotations

import os
import subprocess

from .common import REPO, base_url, load_api_key, run_lang, skip_native, toolchain
from .ts_build import build_client


def _native() -> list[str]:
    node = toolchain("typescript", "node", cwd=str(REPO))
    if not node:
        return skip_native("typescript", "node not installed")
    build, reason = build_client()
    if build is None:
        return skip_native("typescript", reason)
    if build.diagnostics:
        print(f"  WARN {len(build.diagnostics)} pre-existing tsc error(s) in the generated tree")
        for line in build.diagnostics[:3]:
            print(f"       {line.strip()}")
    smoke = REPO / "languages" / "typescript" / "smoke.mjs"
    print("[typescript] node smoke.mjs via the compiled src/client.ts")
    env = os.environ.copy()
    env["INDOX_BASE_URL"] = base_url()
    # Every sibling forwards the key; without it smoke.mjs self-skips and scores PASS.
    env["INDOX_API_KEY"] = load_api_key()
    env["INDOX_TS_CLIENT"] = str(build.entry)
    try:
        proc = subprocess.run([*node, str(smoke)], cwd=str(REPO), env=env, check=False)
    finally:
        build.cleanup()
    if proc.returncode != 0:
        return [f"typescript smoke.mjs exited {proc.returncode}"]
    return []


def test_typescript() -> list[str]:
    return run_lang("typescript", native=_native)


if __name__ == "__main__":
    raise SystemExit(1 if test_typescript() else 0)
