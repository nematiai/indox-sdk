"""The ONE reader of the local smoke-credentials file.

Three copies of this logic drifted apart before (different env var names, only one
of them tightening the file mode), so every caller
resolves credentials through here. Path comes from INDOX_CREDS_FILE.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .env import require_env


def creds_path() -> Path:
    return Path(require_env("INDOX_CREDS_FILE"))


def read_creds(path: Path | None = None) -> dict[str, Any]:
    path = path or creds_path()
    if not path.is_file():
        return {}
    mode = path.stat().st_mode & 0o777
    if mode & 0o077:
        # A raw API key on a shared host must not be group/world readable.
        try:
            path.chmod(0o600)
            print(f"  NOTE tightened {path} {mode:04o} → 0600")
        except OSError as exc:
            print(f"  WARN {path} is {mode:04o} and could not be tightened: {exc}")
    return json.loads(path.read_text(encoding="utf-8"))


def find_api_key(path: Path | None = None) -> str:
    env = (os.environ.get("INDOX_API_KEY") or "").strip()
    if env:
        return env
    data = read_creds(path)
    return (
        data.get("api_key_raw") or data.get("macos_api_key") or data.get("external_token") or ""
    ).strip()


def key_required() -> bool:
    return os.environ.get("INDOX_REQUIRE_KEY", "").strip() == "1"


def missing_key_reason() -> str:
    return f"no INDOX_API_KEY and no key in {creds_path()}"


def load_api_key() -> str:
    key = find_api_key()
    if key:
        return key
    raise SystemExit(f"Set INDOX_API_KEY or {creds_path()}")
