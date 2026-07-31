"""Generate official SDKs via openapi-generator Docker image.

Usage:
  python3 tools/generate_sdk.py --lang typescript
  python3 tools/generate_sdk.py --all
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from openapi_sources import PUBLIC_OUT, REPO  # noqa: E402
from sdk_targets import IMAGE, LANGS, ORDER, git_flags  # noqa: E402

SDK_ROOT = REPO
SCHEMA_IN_CONTAINER = "/local/spec/openapi-public.json"


def _run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def _clear(out: Path) -> None:
    if not out.exists():
        return
    # The generator runs as the invoking uid:gid, so nothing here is root-owned.
    shutil.rmtree(out)


def generate(lang: str) -> Path:
    if lang not in LANGS:
        raise SystemExit(f"Unknown lang {lang!r}; choose from {sorted(LANGS)}")
    if not PUBLIC_OUT.is_file():
        raise SystemExit(f"Missing {PUBLIC_OUT}; run build_openapi_public.py first")

    generator, subdir, props = LANGS[lang]
    out = SDK_ROOT / subdir / "generated"
    _clear(out)
    out.mkdir(parents=True, exist_ok=True)

    cmd = [
        "docker", "run", "--rm",
        "--user", f"{os.getuid()}:{os.getgid()}",
        "-v", f"{REPO}:/local",
        IMAGE, "generate",
        "-i", SCHEMA_IN_CONTAINER,
        "-g", generator,
        "-o", f"/local/{subdir}/generated",
    ]
    cmd.extend(git_flags(lang))
    for p in props:
        cmd.extend(["--additional-properties", p])
    _run(cmd)
    print(f"Generated {lang} → {out}")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", choices=sorted(LANGS))
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.list:
        for k in sorted(LANGS):
            print(k)
        return
    if args.all:
        for lang in ORDER:
            generate(lang)
        return
    if not args.lang:
        raise SystemExit("Pass --lang <id> or --all")
    generate(args.lang)


if __name__ == "__main__":
    main()
