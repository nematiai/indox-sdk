"""The allowlist row type, shared by the parser and the ellipsis table."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AllowlistOp:
    method: str
    path: str
    tier: str
    raw_sdk: str
