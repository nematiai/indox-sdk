"""The ONE package-layout manifest for the official SDKs.

check_packages.py (the gate) and tests/ (the suite) both read this. They used to
keep private copies that had already drifted — the gate demanded a README the suite
did not, so "package-ready" meant two different things.

Paths are repo-relative. `python` is `indox_client/`, which has no <lang>/generated/ tree.
"""
from __future__ import annotations

REQUIRED: dict[str, tuple[str, ...]] = {
    "python": (
        "languages/python/indox_client/__init__.py",
        "languages/python/indox_client/_client.py",
    ),
    "typescript": (
        "languages/typescript/generated/src/index.ts",
        "languages/typescript/src/client.ts",
        "languages/typescript/package.json",
        "languages/typescript/smoke.mjs",
        "languages/typescript/README.md",
    ),
    "php": (
        "languages/php/generated/lib",
        "languages/php/src/IndoxClient.php",
        "languages/php/composer.json",
        "languages/php/README.md",
    ),
    "ruby": (
        "languages/ruby/generated/lib",
        "languages/ruby/lib/indox_client.rb",
        "languages/ruby/indox.gemspec",
        "languages/ruby/README.md",
    ),
    "java": (
        "languages/java/generated/src/main/java",
        "languages/java/src/main/java/org/indox/IndoxClient.java",
        "languages/java/README.md",
    ),
    "dotnet": (
        "languages/dotnet/generated/src",
        "languages/dotnet/src/IndoxClient.cs",
        "languages/dotnet/README.md",
    ),
    "go": (
        "languages/go/generated",
        "languages/go/indox/client.go",
        "languages/go/go.mod",
        "languages/go/README.md",
    ),
    "rust": (
        "languages/rust/generated/src",
        "languages/rust/src/lib.rs",
        "languages/rust/Cargo.toml",
        "languages/rust/README.md",
    ),
}

LANGS = tuple(REQUIRED.keys())
