"""Run a language's native leg in its official container when the host lacks the tool.

One image per language, one container at a time, `--rm` so nothing outlives its
own test. Teardown only ever touches a tag THIS harness pulled.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

from tools.env import REPO, get_env

# Official image per language, major-pinned. SDK_IMAGE_<LANG> overrides one
# without touching code; used only when the toolchain is absent from the host.
TOOLCHAIN_IMAGES: dict[str, str] = {
    "php": "php:8.3-cli",
    "ruby": "ruby:3.3-slim",
    "java": "eclipse-temurin:21-jdk",
    "dotnet": "mcr.microsoft.com/dotnet/sdk:8.0",
    "go": "golang:1.22",
    "rust": "rust:1-slim",
    "typescript": "node:lts",
}

CONTAINER_ENV = ("INDOX_API_KEY", "INDOX_BASE_URL")

# Tags this harness pulled and may therefore remove again — persisted so
# `make test-clean` in a later process can never delete an image it did not fetch.
PULL_MANIFEST = Path(
    get_env("SDK_DOCKER_MANIFEST") or Path(tempfile.gettempdir()) / "indox-sdk-pulled-images.json"
)
USED_IMAGES: set[str] = set()


def docker_fallback_enabled() -> bool:
    return get_env("SDK_DOCKER").lower() in {"1", "true", "yes"}


def image_cleanup_enabled() -> bool:
    return get_env("SDK_DOCKER_CLEAN").lower() in {"1", "true", "yes"}


def image_for(lang: str) -> str:
    return get_env(f"SDK_IMAGE_{lang.upper()}", TOOLCHAIN_IMAGES.get(lang, ""))


def configured_images() -> set[str]:
    return {image_for(lang) for lang in TOOLCHAIN_IMAGES}


@lru_cache(maxsize=1)
def _docker_usable() -> bool:
    if not shutil.which("docker"):
        return False
    return subprocess.run(["docker", "info"], capture_output=True, check=False).returncode == 0


def _docker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["docker", *args], capture_output=True, check=False, text=True)


def _pulled() -> list[str]:
    try:
        data = json.loads(PULL_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [str(i) for i in data] if isinstance(data, list) else []


def _pulled_write(images: list[str]) -> None:
    PULL_MANIFEST.write_text(json.dumps(sorted(set(images))), encoding="utf-8")


def _note_first_use(image: str) -> None:
    USED_IMAGES.add(image)
    # Recorded BEFORE the run that pulls it: an image already on the host
    # belongs to something else and must never be torn down.
    if _docker("image", "inspect", image).returncode != 0:
        _pulled_write([*_pulled(), image])
        print(f"  PULL {image} (absent — fetched by this run)")
    else:
        print(f"  KEEP {image} (present before this run)")


def toolchain(lang: str, tool: str, *, cwd: str | None = None) -> list[str] | None:
    """argv prefix ending in `tool` — the host binary, else its official image, else None."""
    host = shutil.which(tool)
    if host:
        return [host]
    image = image_for(lang)
    if not image or not docker_fallback_enabled() or not _docker_usable():
        return None
    if image not in USED_IMAGES:
        _note_first_use(image)
    # Repo and /tmp are mounted at their own absolute paths so every path the
    # tests already build resolves identically inside the container.
    return [
        "docker", "run", "--rm", "--network", "host",
        "-u", f"{os.getuid()}:{os.getgid()}",
        "-v", f"{REPO}:{REPO}",
        "-v", "/tmp:/tmp",
        "-w", cwd or str(REPO),
        "-e", "HOME=/tmp",
        *[arg for name in CONTAINER_ENV for arg in ("-e", name)],
        image,
        tool,
    ]


def remove_image(image: str) -> str:
    """Remove one exact tag — never a wildcard, a dangling sweep, or a prune."""
    if image not in configured_images():
        return f"refused {image} (not a toolchain image)"
    if image not in _pulled():
        return f"kept {image} (present before this run)"
    proc = _docker("rmi", image)
    if proc.returncode != 0:
        return f"could not remove {image}: {(proc.stderr or proc.stdout).strip().splitlines()[-1]}"
    _pulled_write([i for i in _pulled() if i != image])
    return f"removed {image}"


def teardown_image(lang: str) -> None:
    """Drop this language's image before the next one starts (SDK_DOCKER_CLEAN=1)."""
    image = image_for(lang)
    if not image_cleanup_enabled() or image not in USED_IMAGES:
        return
    USED_IMAGES.discard(image)
    print(f"  CLEAN {remove_image(image)}")


def clean_images() -> int:
    targets = [i for i in _pulled() if i in configured_images()]
    if not targets:
        print("CLEAN nothing to remove — no toolchain image was pulled by these tests")
        return 0
    for image in targets:
        print(f"CLEAN {remove_image(image)}")
    return 0
