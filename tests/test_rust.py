"""Rust SDK tests."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .common import REPO, base_url, load_api_key, run_lang, skip_native


def _native() -> list[str]:
    cargo = shutil.which("cargo")
    if not cargo:
        return skip_native("rust", "cargo not installed")
    key = load_api_key()
    base = base_url()
    crate = REPO / "rust"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "Cargo.toml").write_text(
            f"""
[package]
name = "indox_smoke"
version = "0.1.0"
edition = "2021"

[dependencies]
indox-sdk = {{ path = "{crate.as_posix()}" }}
tokio = {{ version = "1", features = ["rt-multi-thread", "macros"] }}
""".strip(),
            encoding="utf-8",
        )
        (root / "src").mkdir()
        (root / "src" / "main.rs").write_text(
            """
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let c = indox_sdk::Indox::from_env()?;
    let (code, _) = c.health().await?;
    if code >= 500 { return Err(format!("health HTTP {code}").into()); }
    println!("PASS rust IndoxClient health HTTP {code}");
    Ok(())
}
""".strip(),
            encoding="utf-8",
        )
        print("[rust] cargo run Indox::health")
        env = os.environ.copy()
        env["INDOX_API_KEY"] = key
        env["INDOX_BASE_URL"] = base
        proc = subprocess.run(
            [cargo, "run", "-q"],
            cwd=str(root),
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.stdout:
            print(proc.stdout.rstrip())
        if proc.returncode != 0:
            return [f"rust native: {proc.stderr.strip() or proc.returncode}"]
    return []


def test_rust() -> list[str]:
    return run_lang("rust", native=_native)


if __name__ == "__main__":
    raise SystemExit(1 if test_rust() else 0)
