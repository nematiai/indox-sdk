"""openapi-generator targets per official SDK language.

lang id → (generator name, <subdir>/, extra --additional-properties).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from env import require_env  # noqa: E402

GIT_USER = require_env("INDOX_GIT_USER")
SDK_VERSION = require_env("INDOX_SDK_VERSION")
IMAGE = require_env("INDOX_OPENAPI_GENERATOR_IMAGE")


def repo_id(lang: str) -> str:
    return f"indox-{lang}"


GO_MODULE = f"github.com/{GIT_USER}/{repo_id('go')}"


def git_flags(lang: str) -> list[str]:
    """Top-level generator flags — NOT --additional-properties. Unset, every
    generator ships the literal GIT_USER_ID/GIT_REPO_ID placeholder in go.mod,
    docs and tests."""
    return ["--git-user-id", GIT_USER, "--git-repo-id", repo_id(lang)]

LANGS: dict[str, tuple[str, str, list[str]]] = {
    "typescript": (
        "typescript-fetch",
        "typescript",
        [
            "npmName=@indox/sdk",
            f"npmVersion={SDK_VERSION}",
            "supportsES6=true",
            "typescriptThreePlus=true",
            "withInterfaces=true",
        ],
    ),
    "php": (
        "php",
        "php",
        [
            "invokerPackage=Indox",
            "packageName=Indox",
            "composerPackageName=indox/indox",
            f"artifactVersion={SDK_VERSION}",
        ],
    ),
    "ruby": (
        "ruby",
        "ruby",
        [
            "gemName=indox",
            "moduleName=Indox",
            f"gemVersion={SDK_VERSION}",
        ],
    ),
    "java": (
        "java",
        "java",
        [
            "groupId=org.indox",
            "artifactId=indox-sdk",
            f"artifactVersion={SDK_VERSION}",
            "apiPackage=org.indox.api",
            "modelPackage=org.indox.model",
            "invokerPackage=org.indox",
            "library=native",
        ],
    ),
    "dotnet": (
        "csharp",
        "dotnet",
        [
            "packageName=Indox.Sdk",
            f"packageVersion={SDK_VERSION}",
            "targetFramework=net8.0",
            "library=httpclient",
        ],
    ),
    "go": (
        "go",
        "go",
        [
            "packageName=indox",
            f"moduleName={GO_MODULE}",
            "enumClassPrefix=true",
            "isGoSubmodule=false",
        ],
    ),
    "rust": (
        "rust",
        "rust",
        [
            "packageName=indox",
            f"packageVersion={SDK_VERSION}",
            "library=reqwest",
        ],
    ),
}

ORDER = ("typescript", "php", "ruby", "java", "dotnet", "go", "rust")
