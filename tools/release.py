"""Release guards for the Python client — refuse a bad publish before it is permanent.

PyPI never lets a version be reused, so every check here runs BEFORE upload:
  version   the version the build will carry
  taken     that version already exists on PyPI
  dirty     uncommitted changes would ship untracked code
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PY_DIR = REPO / "languages" / "python"
VERSION_FILE = PY_DIR / "indox_client" / "_version.py"
PYPI = "https://pypi.org/pypi/{name}/json"


def current_version() -> str:
    text = VERSION_FILE.read_text(encoding="utf-8")
    return text.split('"')[1]


def published_versions(name: str) -> set[str]:
    try:
        with urllib.request.urlopen(PYPI.format(name=name), timeout=30) as resp:  # noqa: S310
            return set(json.loads(resp.read().decode("utf-8"))["releases"])
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return set()
        raise


def set_version(new: str) -> None:
    VERSION_FILE.write_text(f'__version__ = "{new}"\n', encoding="utf-8")
    print(f"version -> {new}  ({VERSION_FILE.relative_to(REPO)})")


def guard(name: str) -> None:
    version = current_version()
    if version in published_versions(name):
        raise SystemExit(
            f"REFUSING: {name} {version} is already on PyPI and a version can never be "
            f"reused. Bump it first:  make bump SDK_VERSION=<next>"
        )
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(
            "REFUSING: working tree is dirty — commit first so the tag matches what ships.\n"
            + dirty
        )
    print(f"OK release guard: {name} {version} is unpublished, tree is clean")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--name", default="indox-client")
    p.add_argument("--guard", action="store_true")
    p.add_argument("--print-version", action="store_true")
    p.add_argument("--set-version")
    a = p.parse_args()
    if a.set_version:
        set_version(a.set_version)
    elif a.print_version:
        print(current_version())
    elif a.guard:
        guard(a.name)
    else:
        raise SystemExit("Pass --guard, --print-version or --set-version")


if __name__ == "__main__":
    main()
