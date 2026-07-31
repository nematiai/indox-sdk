"""Parse spec/ALLOWLIST.md into structured ops."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from allowlist_ellipsis import _expand_ellipsis  # noqa: E402
from allowlist_types import AllowlistOp  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
ALLOWLIST_PATH = REPO / "spec" / "ALLOWLIST.md"

_ROW = re.compile(
    r"^\|\s*(GET|POST|PUT|PATCH|DELETE|GET/POST/DELETE|\*)\s*\|\s*`([^`]+)`\s*\|\s*([^|]+)\|",
    re.IGNORECASE,
)
_TIER = re.compile(r"\b(P0|P1|P2|P3|P4|ADV)\b", re.IGNORECASE)


# An op row starts with an HTTP-verb cell. ALLOWLIST.md's other tables key on a path or
# an app name, so those are not ops and must not trip the reject.
_CANDIDATE = re.compile(
    r"^\|\s*(?:\*|(?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS|TRACE|CONNECT)"
    r"(?:/(?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS))*)\s*\|[^|]*/api/",
    re.IGNORECASE,
)
_EXCLUDED = re.compile(r"\b(omit|omitted|blocked|internal)\b", re.IGNORECASE)


def _reject(line: str, why: str) -> None:
    raise SystemExit(
        f"ALLOWLIST.md: {why} — {line.strip()[:120]}\n"
        "A row that names an /api/ path must either carry a tier (P0-P4/ADV) or be "
        "explicitly marked omit/blocked/internal. Dropping it silently would remove the "
        "op from the allowlist, the generated spec and the drift gate at once."
    )


def parse_allowlist(path: Path | None = None) -> list[AllowlistOp]:
    text = (path or ALLOWLIST_PATH).read_text(encoding="utf-8")
    ops: list[AllowlistOp] = []
    for line in text.splitlines():
        stripped = line.strip()
        m = _ROW.match(stripped)
        if not m:
            if _CANDIDATE.match(stripped):
                _reject(line, "row names an /api/ path but does not parse")
            continue
        method_raw, api_path, sdk_cell = m.group(1), m.group(2).strip(), m.group(3).strip()
        tier_m = _TIER.search(sdk_cell)
        if not tier_m:
            # Tier is checked BEFORE the marker so prose like "P1 replaces the internal
            # legacy route" cannot drop a real op on a substring match.
            if _EXCLUDED.search(sdk_cell):
                continue
            _reject(line, "row has no tier marker and is not marked omit/blocked/internal")
        tier = tier_m.group(1).upper()
        if tier == "P4":
            continue
        for method in _expand_methods(method_raw):
            ops.append(
                AllowlistOp(
                    method=method, path=_normalize_path(api_path), tier=tier, raw_sdk=sdk_cell
                )
            )
    return ops


def _expand_methods(raw: str) -> list[str]:
    raw = raw.strip().upper()
    if raw == "*":
        return ["GET", "POST", "PUT", "PATCH", "DELETE"]
    if "/" in raw:
        return [p.strip().upper() for p in raw.split("/") if p.strip()]
    return [raw]


def _normalize_path(path: str) -> str:
    path = path.strip()
    # Collapse ellipsis pipeline/scan/signing groups into concrete prefixes later
    if not path.startswith("/"):
        path = "/" + path
    return path


def v1_ops(include_adv: bool = True) -> list[AllowlistOp]:
    ops = parse_allowlist()
    out: list[AllowlistOp] = []
    for op in ops:
        if op.tier == "ADV" and not include_adv:
            continue
        if "…" in op.path or "..." in op.path:
            # Expand known ADV prefix groups from ALLOWLIST
            for concrete in _expand_ellipsis(op):
                out.append(concrete)
            continue
        out.append(op)
    return _dedupe(out)


def _dedupe(ops: list[AllowlistOp]) -> list[AllowlistOp]:
    seen: set[tuple[str, str]] = set()
    out: list[AllowlistOp] = []
    for op in ops:
        key = (op.method, op.path)
        if key in seen:
            continue
        seen.add(key)
        out.append(op)
    return out
