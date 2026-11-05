"""Find `better4nix-frontend-<lang>` executables on PATH."""

from __future__ import annotations

import shutil

PREFIX = "better4nix-frontend-"


def find_frontend(ext: str) -> str | None:
    """Return the path to the frontend executable for the given extension, or None."""
    if not ext:
        return None
    name = PREFIX + ext.lstrip(".").lower()
    return shutil.which(name)


def supported_extensions() -> list[str]:
    """List extensions whose frontend is currently installed."""
    exts: list[str] = []
    for d in _path_dirs():
        try:
            for entry in __import__("os").listdir(d):
                if entry.startswith(PREFIX):
                    exts.append(entry[len(PREFIX):])
        except OSError:
            continue
    return sorted(set(exts))


def _path_dirs() -> list[str]:
    import os
    return [p for p in os.environ.get("PATH", "").split(os.pathsep) if p]