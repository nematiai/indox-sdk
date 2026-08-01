"""Run a language's native leg in its official container when the host lacks the tool.

One image per language, one container at a time, `--rm` so nothing outlives its
own test. Teardown only ever touches a tag THIS process pulled itself.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from functools import lru_cache

from tools.env import REPO, get_env

# Official image per language, major-pinned. SDK_IMAGE_<LANG> overrides which
# image is RUN, never which image may be removed; used only when the toolchain
# is absent from the host.
TOOLCHAIN_IMAGES: dict[str, str] = {
    "php": "php:8.3-cli",
    "ruby": "ruby:3.3-slim",
    "java": "eclipse-temurin:21-jdk",
    "dotnet": "mcr.microsoft.com/dotnet/sdk:8.0",
    "go": "golang:1.22",
    "rust": "rust:1-slim",
    "typescript": "node:lts",
}

CONTAINER_ENV = ("INDOX_API_KEY", "INDOX_BASE_URL", "INDOX_TS_CLIENT")

# The only removable set, fixed in code: an env var can redirect which image a
# language runs, so an env-derived table would let anything on the host qualify.
REMOVABLE_IMAGES: frozenset[str] = frozenset(TOOLCHAIN_IMAGES.values())

# Provenance is in-memory and process-local on purpose. Persisting it would let
# any other process assert "this run pulled X" and earn a deletion.
PULLED_HERE: set[str] = set()
PRESENT_BEFORE: set[str] = set()
USED_IMAGES: set[str] = set()


def docker_fallback_enabled() -> bool:
    return get_env("SDK_DOCKER").lower() in {"1", "true", "yes"}


def image_cleanup_enabled() -> bool:
    return get_env("SDK_DOCKER_CLEAN").lower() in {"1", "true", "yes"}


def image_for(lang: str) -> str:
    return get_env(f"SDK_IMAGE_{lang.upper()}", TOOLCHAIN_IMAGES.get(lang, ""))


@lru_cache(maxsize=1)
def _docker_usable() -> bool:
    if not shutil.which("docker"):
        return False
    return subprocess.run(["docker", "info"], capture_output=True, check=False).returncode == 0


def _docker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["docker", *args], capture_output=True, check=False, text=True)


def _on_host(image: str) -> bool:
    return _docker("image", "inspect", image).returncode == 0


def _note_first_use(image: str) -> None:
    USED_IMAGES.add(image)
    # Decided BEFORE the run that pulls it, and binding for the whole process:
    # an image already on the host belongs to something else, forever.
    if _on_host(image):
        PRESENT_BEFORE.add(image)
        print(f"  KEEP {image} (present before this run)")
    else:
        PULLED_HERE.add(image)
        print(f"  PULL {image} (absent — fetched by this run)")


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
    if image not in REMOVABLE_IMAGES:
        return f"refused {image} (not a built-in toolchain image)"
    if image in PRESENT_BEFORE:
        return f"kept {image} (present before this run)"
    if image not in PULLED_HERE:
        return f"kept {image} (this process did not pull it)"
    proc = _docker("rmi", image)
    if proc.returncode != 0:
        return f"could not remove {image}: {(proc.stderr or proc.stdout).strip().splitlines()[-1]}"
    PULLED_HERE.discard(image)
    return f"removed {image}"


def teardown_image(lang: str) -> None:
    """Drop this language's image before the next one starts (SDK_DOCKER_CLEAN=1)."""
    image = image_for(lang)
    if not image_cleanup_enabled() or image not in USED_IMAGES:
        return
    USED_IMAGES.discard(image)
    print(f"  CLEAN {remove_image(image)}")


def clean_images() -> int:
    """Report which toolchain tags are on the host. Removes nothing, ever."""
    print("CLEAN reports only — it does not remove anything.")
    print("Whether these tests pulled an image is known only inside the process that")
    print("pulled it; a later run cannot prove it, so it must not delete on a guess.")
    if not _docker_usable():
        print("  docker is not usable here — nothing to report")
        return 0
    present = [i for i in sorted(REMOVABLE_IMAGES) if _on_host(i)]
    if not present:
        print("  no toolchain image is on this host")
        return 0
    for image in present:
        print(f"  present {image}")
    print("\nRemove them yourself only if nothing else on this host needs them:")
    print(f"  docker rmi {' '.join(present)}")
    return 0
