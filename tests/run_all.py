"""Run SDK tests for every official language.

Usage (repo root):
  PYTHONPATH=. python3 -m tests.run_all
  PYTHONPATH=. python3 -m tests.run_all --lang typescript
  make sdk-test
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Allow `python3 tests/run_all.py` without PYTHONPATH=.
_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from tests.common import LANGS, SKIPPED_NATIVE  # noqa: E402
from tools.creds import find_api_key, key_required, missing_key_reason  # noqa: E402
from tests.test_dotnet import test_dotnet  # noqa: E402
from tests.test_go import test_go  # noqa: E402
from tests.test_java import test_java  # noqa: E402
from tests.test_php import test_php  # noqa: E402
from tests.test_python import test_python  # noqa: E402
from tests.test_ruby import test_ruby  # noqa: E402
from tests.test_rust import test_rust  # noqa: E402
from tests.test_typescript import test_typescript  # noqa: E402

EXIT_UNVERIFIED = 3

RUNNERS = {
    "python": test_python,
    "typescript": test_typescript,
    "php": test_php,
    "ruby": test_ruby,
    "java": test_java,
    "dotnet": test_dotnet,
    "go": test_go,
    "rust": test_rust,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lang",
        choices=sorted(RUNNERS),
        action="append",
        help="Run one language (repeatable). Default: all.",
    )
    parser.add_argument(
        "--skip-python-allowlist",
        action="store_true",
        help="Skip the 79-probe Python allowlist (faster CI loop).",
    )
    args = parser.parse_args(argv)

    if args.skip_python_allowlist:
        os.environ["SDK_TEST_SKIP_PYTHON_ALLOWLIST"] = "1"

    if not find_api_key():
        reason = missing_key_reason()
        if key_required():
            print(f"FAIL sdk tests: {reason}")
            return 1
        # Exit 3 (UNVERIFIED), never 0: nothing ran, so no caller may read this as a pass.
        print(f"SKIP sdk tests — NOTHING VERIFIED: {reason}")
        return EXIT_UNVERIFIED

    langs = args.lang or list(LANGS)
    summary: list[tuple[str, str]] = []
    any_fail = False
    for lang in langs:
        print("=" * 60)
        print(f"LANG {lang}")
        print("=" * 60)
        fails = RUNNERS[lang]()
        if fails:
            any_fail = True
            summary.append((lang, "FAIL"))
            for f in fails:
                print(f"  !! {f}")
        else:
            summary.append((lang, "SKIP" if lang in SKIPPED_NATIVE else "PASS"))
        print()

    print("=" * 60)
    print("SUMMARY")
    for lang, status in summary:
        note = f"   (native not run: {SKIPPED_NATIVE[lang]})" if lang in SKIPPED_NATIVE else ""
        print(f"  {status:4} {lang}{note}")
    verified = sum(1 for _, s in summary if s == "PASS")
    skipped = sum(1 for _, s in summary if s == "SKIP")
    print("-" * 60)
    print(f"  {verified} fully verified · {skipped} HTTP-only (native leg not run) · {len(summary)} total")
    if skipped:
        print("  NOTE a SKIP verified the package layout and HTTP reachability only.")
    print("=" * 60)
    if skipped and os.environ.get("INDOX_REQUIRE_NATIVE", "").strip() == "1":
        print("FAIL INDOX_REQUIRE_NATIVE=1 and "
              f"{skipped} language(s) could not run their native leg")
        return 1
    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
