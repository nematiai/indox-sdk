"""Shared helpers for tests/ — package layout + allowlist HTTP probes."""
from __future__ import annotations

import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

from tools.creds import load_api_key  # noqa: F401
from tools.env import require_env
from tools.packages import LANGS, REQUIRED  # noqa: F401

from .toolchain import (  # noqa: F401
    TOOLCHAIN_IMAGES,
    clean_images,
    teardown_image,
    toolchain,
)

REPO = Path(__file__).resolve().parents[1]
SDK = REPO
SOFT = {400, 401, 403, 404, 405, 409, 415, 422, 429}

# Core convert probes every language client must be able to hit.
PROBES: tuple[tuple[str, str], ...] = (
    ("health", "/api/v1/health/"),
    ("fonts.formats", "/api/v1/fonts/formats/"),
    ("pdf.formats", "/api/v1/pdf_handler/formats/"),
    ("image.formats", "/api/v1/convert/image/formats/"),
    ("video.formats", "/api/v1/convert/video/formats/"),
    ("model.formats", "/api/v1/convert/model/formats/"),
    ("webhooks.list", "/api/v1/webhooks/"),
    ("billing.credits", "/api/v1/subscription/credits/balance/"),
)

PACKAGE_REQUIRED = REQUIRED


def base_url() -> str:
    return require_env("INDOX_BASE_URL").rstrip("/")


def check_package(lang: str) -> list[str]:
    misses: list[str] = []
    for rel in PACKAGE_REQUIRED[lang]:
        if not (REPO / rel).exists():
            misses.append(rel)
    return misses


def http_get(path: str, *, key: str, base: str) -> int:
    req = urllib.request.Request(
        f"{base}{path}",
        headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            return int(resp.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)


def run_http_probes(lang: str, *, key: str | None = None, base: str | None = None) -> list[str]:
    key = key or load_api_key()
    base = base or base_url()
    failures: list[str] = []
    print(f"[{lang}] HTTP smoke base={base}")
    for label, path in PROBES:
        try:
            status = http_get(path, key=key, base=base)
        except Exception as exc:  # noqa: BLE001
            msg = f"{label}: {exc}"
            print(f"  FAIL {msg}")
            failures.append(msg)
            continue
        if status >= 500:
            msg = f"{label}: HTTP {status}"
            print(f"  FAIL {msg}")
            failures.append(msg)
        elif status >= 400 and status not in SOFT:
            msg = f"{label}: unexpected HTTP {status}"
            print(f"  FAIL {msg}")
            failures.append(msg)
        else:
            print(f"  PASS {label} (HTTP {status})")
    return failures


SKIPPED_NATIVE: dict[str, str] = {}


def skip_native(lang: str, reason: str) -> list[str]:
    """Record that a language's native leg did NOT run.

    Returning [] alone reads as PASS, so an absent toolchain used to look
    identical to a verified client.
    """
    SKIPPED_NATIVE[lang] = reason
    print(f"  SKIP native {lang} ({reason})")
    return []


def run_lang(
    lang: str,
    *,
    native: Callable[[], list[str]] | None = None,
) -> list[str]:
    failures: list[str] = []
    misses = check_package(lang)
    if misses:
        for m in misses:
            print(f"  FAIL missing {m}")
            failures.append(f"missing {m}")
        return failures
    print(f"  OK package layout ({lang})")
    failures.extend(run_http_probes(lang))
    if native is not None:
        failures.extend(native())
    return failures
