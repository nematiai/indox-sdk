"""CI entry: optional rebuild, drift, package layout, fast multi-lang SDK tests."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOLS = Path(__file__).resolve().parent


def _run(cmd: list[str], gate: str, env: dict[str, str] | None = None) -> None:
    # flush: piped stdout would otherwise print all the echoes after all the output,
    # attributing each gate's result to the wrong command in a CI log.
    print("+", " ".join(cmd), flush=True)
    rc = subprocess.run(cmd, cwd=REPO, env=env).returncode
    if rc != 0:
        print(f"FAIL sdk CI gate: {gate} (exit {rc})", file=sys.stderr)
        raise SystemExit(rc)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild", action="store_true", help="Rebuild openapi-public.json first")
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip the HTTP suite",
    )
    args = parser.parse_args()
    if args.rebuild:
        _run([sys.executable, str(TOOLS / "build_openapi_public.py")], "openapi rebuild")
    _run([sys.executable, str(TOOLS / "check_drift.py")], "schema drift")
    _run([sys.executable, str(TOOLS / "check_packages.py")], "package layout")
    if not args.skip_tests:
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{REPO}{os.pathsep}{env.get('PYTHONPATH', '')}"
        # Fast by default in CI gates — full Python allowlist via `make sdk-test`.
        _run(
            [
                sys.executable,
                "-m",
                "tests.run_all",
                "--skip-python-allowlist",
            ],
            "multi-language tests",
            env=env,
        )
    print("OK sdk CI gates")


if __name__ == "__main__":
    main()
