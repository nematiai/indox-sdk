"""Compile the hand-written TypeScript client so a smoke can actually import it.

`src/client.ts` is TypeScript and the generated tree uses extensionless relative
imports, so the only runnable form is a CommonJS emit. Output goes to a private
0700 temp dir, never a predictable path: the smoke *executes* what lands there.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from tools.env import REPO, get_env

from .toolchain import toolchain

TS_DIR = REPO / "languages" / "typescript"
CLIENT_ENTRY = Path("src") / "client.js"
NPM_SPECS = (
    get_env("SDK_TS_COMPILER", "typescript@5"),
    get_env("SDK_TS_NODE_TYPES", "@types/node@20"),
)


def _tsconfig(scratch: Path) -> dict[str, object]:
    return {
        "compilerOptions": {
            "target": "es2022",
            "module": "commonjs",
            "moduleResolution": "node",
            "outDir": str(scratch / "out"),
            "rootDir": str(TS_DIR),
            "esModuleInterop": True,
            "skipLibCheck": True,
            "lib": ["es2022", "dom"],
            "typeRoots": [str(scratch / "node_modules" / "@types")],
        },
        "include": [
            f"{TS_DIR}/src/**/*.ts",
            f"{TS_DIR}/generated/src/**/*.ts",
        ],
    }


def _run(argv: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, check=False)


class BuildResult:
    def __init__(self, scratch: Path, entry: Path, diagnostics: list[str]) -> None:
        self.scratch = scratch
        self.entry = entry
        self.diagnostics = diagnostics

    def cleanup(self) -> None:
        shutil.rmtree(self.scratch, ignore_errors=True)


def build_client() -> tuple[BuildResult | None, str]:
    """(result, reason). result is None when the client could not be built."""
    npm = toolchain("typescript", "npm", cwd=str(TS_DIR))
    node = toolchain("typescript", "node", cwd=str(TS_DIR))
    if not npm or not node:
        return None, "npm/node not available (host or SDK_DOCKER=1)"
    if not (TS_DIR / "generated" / "src" / "index.ts").is_file():
        return None, "languages/typescript/generated is missing — run `make gen-all`"

    scratch = Path(tempfile.mkdtemp(prefix="indox-sdk-ts-"))
    install = _run(
        [*npm, "install", "--prefix", str(scratch), "--no-audit", "--no-fund",
         "--loglevel=error", *NPM_SPECS],
        cwd=scratch,
    )
    if install.returncode != 0:
        shutil.rmtree(scratch, ignore_errors=True)
        tail = (install.stderr or install.stdout).strip().splitlines()[-1:] or ["no output"]
        return None, f"could not install the TypeScript compiler: {tail[0]}"

    config = scratch / "tsconfig.json"
    config.write_text(json.dumps(_tsconfig(scratch)), encoding="utf-8")
    compile_proc = _run(
        [*node, str(scratch / "node_modules" / "typescript" / "bin" / "tsc"), "-p", str(config)],
        cwd=scratch,
    )
    entry = scratch / "out" / CLIENT_ENTRY
    if not entry.is_file():
        shutil.rmtree(scratch, ignore_errors=True)
        tail = (compile_proc.stdout or compile_proc.stderr).strip().splitlines()[-1:] or ["no output"]
        return None, f"tsc emitted no client: {tail[0]}"

    (scratch / "out" / "package.json").write_text('{"type":"commonjs"}', encoding="utf-8")
    diagnostics = [ln for ln in compile_proc.stdout.splitlines() if ": error TS" in ln]
    return BuildResult(scratch, entry, diagnostics), "built"
