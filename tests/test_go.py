"""Go SDK tests."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from tools.sdk_targets import GO_MODULE

from .common import REPO, base_url, load_api_key, run_lang, skip_native


def _native() -> list[str]:
    go = shutil.which("go")
    if not go:
        return skip_native("go", "go not installed")
    key = load_api_key()
    base = base_url()
    mod = REPO / "languages" / "go"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "go.mod").write_text(
            f"module indoxsmoke\n\ngo 1.22\n\nreplace {GO_MODULE} => {mod.as_posix()}\n\n"
            f"require {GO_MODULE} v0.0.0\n",
            encoding="utf-8",
        )
        (root / "main.go").write_text(
            """
package main

import (
  "fmt"
  "os"
  "__GO_MODULE__/indox"
)

func main() {
  c, err := indox.NewFromEnv()
  if err != nil { panic(err) }
  code, _, err := c.Health()
  if err != nil { panic(err) }
  if code >= 500 { panic(fmt.Sprintf("health HTTP %d", code)) }
  fmt.Printf("PASS go IndoxClient health HTTP %d\\n", code)
}
""".strip().replace("__GO_MODULE__", GO_MODULE),
            encoding="utf-8",
        )
        print("[go] IndoxClient health")
        env = os.environ.copy()
        env["INDOX_API_KEY"] = key
        env["INDOX_BASE_URL"] = base
        for cmd in (
            [go, "mod", "tidy"],
            [go, "run", "."],
        ):
            proc = subprocess.run(
                cmd,
                cwd=str(root),
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                return [f"go {' '.join(cmd[1:])}: {proc.stderr.strip() or proc.returncode}"]
            if proc.stdout and cmd[1] == "run":
                print(proc.stdout.rstrip())
    return []


def test_go() -> list[str]:
    return run_lang("go", native=_native)


if __name__ == "__main__":
    raise SystemExit(1 if test_go() else 0)
