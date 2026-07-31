"""Live verification for indox_client against a running backend.

Run:
    INDOX_BASE_URL=http://localhost:41000 python backend/tests/test_indox_client_sdk.py
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from indox_client import Indox  # noqa: E402

FIXTURE = REPO_ROOT / "backend/tests/fonts/fixtures/Roboto-Regular.ttf"
BASE_URL = os.getenv("INDOX_BASE_URL", "http://localhost:41000")


def main() -> int:
    if not FIXTURE.is_file():
        print(f"FAIL missing fixture: {FIXTURE}")
        return 2

    client = Indox(base_url=BASE_URL)
    try:
        formats = client.fonts.formats.list()
        assert formats.get("service") == "fonts", formats
        print(f"OK formats.list service={formats['service']} routes={formats.get('total_routes')}")

        quota = client.fonts.quota()
        print(f"OK fonts.quota user_type={quota.get('user_type')}")

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "Roboto-Regular.woff2"
            path = client.fonts.convert_and_download(
                FIXTURE,
                target_format="woff2",
                output_path=out,
                timeout=90.0,
            )
            magic = path.read_bytes()[:4]
            assert magic == b"wOF2", magic
            print(f"OK convert_and_download -> {path} ({path.stat().st_size} bytes)")
    finally:
        client.close()

    print("PASS indox_client SDK live test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
