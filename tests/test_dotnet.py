"""C# / .NET SDK tests — layout + HTTP; dotnet when SDK present."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .common import REPO, base_url, load_api_key, run_lang, skip_native


def _native() -> list[str]:
    dotnet = shutil.which("dotnet")
    if not dotnet:
        return skip_native("dotnet", "dotnet not installed")
    key = load_api_key()
    base = base_url()
    src = (REPO / "languages" / "dotnet" / "src" / "IndoxClient.cs").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "Smoke.csproj").write_text(
            """
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
""".strip(),
            encoding="utf-8",
        )
        (root / "IndoxClient.cs").write_text(src, encoding="utf-8")
        (root / "Program.cs").write_text(
            """
using Indox.Sdk;
var c = new IndoxClient();
using var http = c.CreateHttpClient();
var res = await http.GetAsync("api/v1/health/");
var code = (int)res.StatusCode;
if (code >= 500) throw new Exception($"health HTTP {code}");
Console.WriteLine($"PASS csharp IndoxClient health HTTP {code}");
""".strip(),
            encoding="utf-8",
        )
        print("[dotnet] build+run IndoxClient")
        env = os.environ.copy()
        env["INDOX_API_KEY"] = key
        env["INDOX_BASE_URL"] = base
        proc = subprocess.run(
            [dotnet, "run", "--nologo", "-v", "q"],
            cwd=str(root),
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.stdout:
            print(proc.stdout.rstrip())
        if proc.returncode != 0:
            return [f"dotnet native: {proc.stderr.strip() or proc.stdout.strip() or proc.returncode}"]
    return []


def test_dotnet() -> list[str]:
    return run_lang("dotnet", native=_native)


if __name__ == "__main__":
    raise SystemExit(1 if test_dotnet() else 0)
