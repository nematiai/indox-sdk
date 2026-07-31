"""Allowlist coverage smoke for indox_client 0.4.0 (API v1 P0–P3 + PDF ADV).

Empty-body / fake-id probes: HTTP 400/401/403/404/422 = PASS (routed).
HTTP ≥500 = FAIL.

  make smoke     (or: PYTHONPATH=. python3 tests/allowlist_smoke.py)
    (INDOX_BASE_URL / INDOX_CREDS_FILE come from .env; env vars override.)
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.creds import load_api_key  # noqa: E402
from tools.env import require_env  # noqa: E402

sys.path.insert(0, str(REPO / "languages" / "python"))

from indox_client import Indox, __version__  # noqa: E402
from indox_client._exceptions import APIStatusError  # noqa: E402

_UUID = "00000000-0000-0000-0000-000000000000"
_DOWNLOAD_SCRATCH = Path(tempfile.gettempdir()) / "indox-sdk-dl.bin"
OK_SOFT = {400, 401, 403, 404, 405, 409, 415, 422, 429}


def _load_key() -> str:
    return load_api_key()


def _probe(label: str, fn: Callable[[], Any], failures: list[str]) -> None:
    try:
        fn()
        print(f"  PASS {label}")
    except APIStatusError as exc:
        if exc.status_code in OK_SOFT:
            print(f"  PASS {label} (HTTP {exc.status_code})")
        else:
            msg = f"{label}: HTTP {exc.status_code} {exc}"
            print(f"  FAIL {msg}")
            failures.append(msg)
    except Exception as exc:  # noqa: BLE001
        msg = f"{label}: {exc}"
        print(f"  FAIL {msg}")
        failures.append(msg)


def main() -> None:
    base = require_env("INDOX_BASE_URL").rstrip("/")
    key = _load_key()
    failures: list[str] = []
    print(f"indox_client {__version__} allowlist smoke base={base}")

    with Indox(api_key=key, base_url=base) as c:
        # P0
        _probe("health.get", c.health.get, failures)
        _probe("fonts.formats.list", c.fonts.formats.list, failures)
        _probe("fonts.formats.get pdf", lambda: c.fonts.formats.get("ttf"), failures)
        _probe("fonts.quota", c.fonts.quota, failures)
        _probe("fonts.health", c.fonts.health, failures)
        _probe("pdf.formats", c.pdf.formats, failures)
        _probe("pdf.operations", c.pdf.operations, failures)
        _probe("pdf.history", c.pdf.history, failures)
        _probe("pdf.convert_json", lambda: c.pdf.convert_json({}), failures)
        _probe("pdf.form_fields", lambda: c.pdf.form_fields({}), failures)
        _probe("pdf.get", lambda: c.pdf.get(_UUID), failures)
        _probe("pdf.download", lambda: c.pdf.download(_UUID, str(_DOWNLOAD_SCRATCH)), failures)
        _probe("pdf.list_pipelines", c.pdf.list_pipelines, failures)
        _probe("pdf.create_pipeline", lambda: c.pdf.create_pipeline({}), failures)
        _probe("pdf.get_pipeline", lambda: c.pdf.get_pipeline(_UUID), failures)
        _probe("pdf.delete_pipeline", lambda: c.pdf.delete_pipeline(_UUID), failures)
        _probe("pdf.run_pipeline", lambda: c.pdf.run_pipeline(_UUID), failures)
        _probe("pdf.create_scan_session", c.pdf.create_scan_session, failures)
        _probe("pdf.get_scan_session", lambda: c.pdf.get_scan_session(_UUID), failures)
        _probe("pdf.finalize_scan_session", lambda: c.pdf.finalize_scan_session(_UUID), failures)
        _probe("pdf.get_scan_pair", c.pdf.get_scan_pair, failures)
        _probe("pdf.upload_scan_pair_page", lambda: c.pdf.upload_scan_pair_page({}), failures)
        _probe("pdf.delete_scan_pair_page", lambda: c.pdf.delete_scan_pair_page(_UUID), failures)
        _probe("pdf.create_signing_session", lambda: c.pdf.create_signing_session({}), failures)
        _probe("pdf.get_signing_session", lambda: c.pdf.get_signing_session(_UUID), failures)
        _probe("pdf.get_sign_token", lambda: c.pdf.get_sign_token(_UUID), failures)
        _probe("pdf.submit_sign", lambda: c.pdf.submit_sign(_UUID, {}), failures)
        _probe("pdf.decline_sign", lambda: c.pdf.decline_sign(_UUID), failures)
        _probe("docs.credits", c.docs.credits, failures)
        _probe("docs.get", lambda: c.docs.get(_UUID), failures)
        _probe("docs.batch_collect", lambda: c.docs.batch_collect({}), failures)
        _probe("docs.hide", lambda: c.docs.hide({}), failures)
        _probe("media.health", c.media.health, failures)
        _probe("media.credits", c.media.credits, failures)
        _probe("media.get", lambda: c.media.get(_UUID), failures)
        _probe("media.batch_collect", lambda: c.media.batch_collect({}), failures)
        _probe("media.hide", lambda: c.media.hide({}), failures)
        _probe("images.formats", c.images.formats, failures)
        _probe("images.operations", c.images.operations, failures)
        _probe("images.history", c.images.history, failures)
        _probe("images.convert", lambda: c.images.convert(), failures)
        _probe("images.get", lambda: c.images.get(_UUID), failures)
        _probe("videos.formats", c.videos.formats, failures)
        _probe("videos.convert", lambda: c.videos.convert(), failures)
        _probe("models.formats", c.models.formats, failures)
        _probe("models.operations", c.models.operations, failures)
        _probe("models.convert", lambda: c.models.convert(), failures)
        _probe("models.get", lambda: c.models.get(_UUID), failures)
        # P1
        _probe("webhooks.list", c.webhooks.list, failures)
        _probe("webhooks.create", lambda: c.webhooks.create({}), failures)
        _probe("webhooks.get", lambda: c.webhooks.get(_UUID), failures)
        _probe("webhooks.update", lambda: c.webhooks.update(_UUID, {}), failures)
        _probe("webhooks.delete", lambda: c.webhooks.delete(_UUID), failures)
        _probe("webhooks.deliveries", lambda: c.webhooks.deliveries(_UUID), failures)
        _probe("webhooks.test", lambda: c.webhooks.test(_UUID), failures)
        # P2
        _probe("user.me", c.user.me, failures)
        _probe("user.update_me", lambda: c.user.update_me({}), failures)
        _probe("user.list_files", c.user.list_files, failures)
        _probe("user.register_file", lambda: c.user.register_file({}), failures)
        _probe("user.delete_files", lambda: c.user.delete_files({}), failures)
        _probe("user.usage", c.user.usage, failures)
        _probe("user.usage_summary", c.user.usage_summary, failures)
        _probe("user.usage_trend", c.user.usage_trend, failures)
        _probe("user.recent_conversions", c.user.recent_conversions, failures)
        _probe("user.conversion_usage", lambda: c.user.conversion_usage(_UUID), failures)
        _probe("user.list_shares", c.user.list_shares, failures)
        _probe("user.create_share", lambda: c.user.create_share({}), failures)
        _probe("user.delete_share", lambda: c.user.delete_share(_UUID), failures)
        _probe("user.public_share", lambda: c.user.public_share(str(uuid4())), failures)
        # P3
        _probe("billing.credits_balance", c.billing.credits_balance, failures)
        _probe("billing.redeem_promo", lambda: c.billing.redeem_promo("X"), failures)
        _probe("billing.pricing_plans", c.billing.pricing_plans, failures)
        _probe("billing.purchase_initiate", lambda: c.billing.purchase_initiate({}), failures)
        _probe("billing.purchase_pay_as_you_go", lambda: c.billing.purchase_pay_as_you_go({}), failures)
        _probe("billing.purchase_history", c.billing.purchase_history, failures)
        _probe("billing.storage_initiate", lambda: c.billing.storage_initiate({}), failures)
        _probe("billing.task_completion", lambda: c.billing.task_completion({}), failures)
        _probe("billing.task_history", c.billing.task_history, failures)

    if failures:
        print(f"\nFAIL {len(failures)} probe(s)")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print(f"\nPASS indox_client {__version__} allowlist coverage (no 5xx)")


if __name__ == "__main__":
    main()
