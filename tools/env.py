"""Config for the SDK tooling — sourced from the repo-root .env, never a literal.

Process env wins over the file so CI and one-off overrides still work. A key that
is set nowhere is a hard error: a silent built-in default is how a developer URL
ends up baked into a published client.
"""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ENV_FILE = Path(os.environ.get("INDOX_ENV_FILE") or (REPO / ".env"))


def _from_env_file(key: str) -> str:
    if not ENV_FILE.is_file():
        return ""
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        if name.strip() == key:
            return value.strip().strip('"').strip("'")
    return ""


def get_env(key: str, default: str = "") -> str:
    return (os.environ.get(key) or "").strip() or _from_env_file(key) or default


def require_env(key: str) -> str:
    value = get_env(key)
    if not value:
        raise SystemExit(f"Set {key} in the environment or in {ENV_FILE}")
    return value
