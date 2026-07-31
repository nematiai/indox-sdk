"""PHP SDK tests."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .common import REPO, base_url, load_api_key, run_lang, skip_native


def _native() -> list[str]:
    php = shutil.which("php")
    if not php:
        return skip_native("php", "php not installed")
    key = load_api_key()
    base = base_url()
    client = (REPO / "languages" / "php" / "src" / "IndoxClient.php").as_posix()
    script = f"""<?php
require '{client}';
putenv('INDOX_API_KEY={key}');
putenv('INDOX_BASE_URL={base}');
$c = Indox\\IndoxClient::fromEnv();
$hdr = [];
foreach ($c->authHeaders() as $k => $v) {{ $hdr[] = "$k: $v"; }}
$ch = curl_init(rtrim($c->baseUrl, '/').'/api/v1/health/');
curl_setopt_array($ch, [
  CURLOPT_HTTPHEADER => $hdr,
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_TIMEOUT => 30,
]);
curl_exec($ch);
$code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);
if ($code >= 500) {{ fwrite(STDERR, "health HTTP $code\\n"); exit(1); }}
echo "PASS php IndoxClient health HTTP $code\\n";
"""
    print("[php] IndoxClient health")
    with tempfile.NamedTemporaryFile("w", suffix=".php", delete=False) as fh:
        fh.write(script)
        path = Path(fh.name)
    try:
        proc = subprocess.run(
            [php, str(path)],
            env=os.environ.copy(),
            check=False,
            capture_output=True,
            text=True,
        )
    finally:
        path.unlink(missing_ok=True)
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.returncode != 0:
        return [f"php native: {proc.stderr.strip() or proc.returncode}"]
    return []


def test_php() -> list[str]:
    return run_lang("php", native=_native)


if __name__ == "__main__":
    raise SystemExit(1 if test_php() else 0)
