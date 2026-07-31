"""The ONE package-layout manifest for the official SDKs.

check_packages.py (the gate) and tests/ (the suite) both read this. They used to
keep private copies that had already drifted — the gate demanded a README the suite
did not, so "package-ready" meant two different things.

Paths are repo-relative. `python` is `indox_client/`, which has no <lang>/generated/ tree.
"""
from __future__ import annotations

REQUIRED: dict[str, tuple[str, ...]] = {
    "python": (
        "indox_client/__init__.py",
        "indox_client/_client.py",
    ),
    "typescript": (
        "typescript/generated/src/index.ts",
        "typescript/src/client.ts",
        "typescript/package.json",
        "typescript/smoke.mjs",
        "typescript/README.md",
    ),
    "php": (
        "php/generated/lib",
        "php/src/IndoxClient.php",
        "php/composer.json",
        "php/README.md",
    ),
    "ruby": (
        "ruby/generated/lib",
        "ruby/lib/indox_client.rb",
        "ruby/indox.gemspec",
        "ruby/README.md",
    ),
    "java": (
        "java/generated/src/main/java",
        "java/src/main/java/org/indox/IndoxClient.java",
        "java/README.md",
    ),
    "dotnet": (
        "dotnet/generated/src",
        "dotnet/src/IndoxClient.cs",
        "dotnet/README.md",
    ),
    "go": (
        "go/generated",
        "go/indox/client.go",
        "go/go.mod",
        "go/README.md",
    ),
    "rust": (
        "rust/generated/src",
        "rust/src/lib.rs",
        "rust/Cargo.toml",
        "rust/README.md",
    ),
}

LANGS = tuple(REQUIRED.keys())
