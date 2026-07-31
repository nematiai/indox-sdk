"""Ruby SDK tests."""
from __future__ import annotations

import os
import shutil
import subprocess

from .common import REPO, base_url, load_api_key, run_lang, skip_native


def _native() -> list[str]:
    ruby = shutil.which("ruby")
    if not ruby:
        return skip_native("ruby", "ruby not installed")
    lib = REPO / "languages" / "ruby" / "lib" / "indox_client.rb"
    key = load_api_key()
    base = base_url()
    code = f"""
require {str(lib)!r}
ENV['INDOX_API_KEY'] = {key!r}
ENV['INDOX_BASE_URL'] = {base!r}
c = IndoxClient::Client.new
res = c.health
raise "health HTTP #{{res.code}}" if res.code.to_i >= 500
puts "PASS ruby IndoxClient health HTTP #{{res.code}}"
"""
    print("[ruby] IndoxClient health")
    proc = subprocess.run(
        [ruby, "-e", code],
        env=os.environ.copy(),
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.returncode != 0:
        return [f"ruby native: {proc.stderr.strip() or proc.returncode}"]
    return []


def test_ruby() -> list[str]:
    return run_lang("ruby", native=_native)


if __name__ == "__main__":
    raise SystemExit(1 if test_ruby() else 0)
