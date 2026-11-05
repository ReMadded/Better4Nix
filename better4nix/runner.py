"""Run a frontend plugin as a subprocess and parse its JSON AST output."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .schema import ASTError, validate


class FrontendError(Exception):
    """A frontend failed or produced an invalid AST."""


def run_frontend(executable: str, source_path: Path) -> dict:
    """Invoke the frontend on `source_path`, validate the resulting AST, return it."""
    try:
        proc = subprocess.run(
            [executable, str(source_path)],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as e:
        raise FrontendError(f"failed to run frontend {executable!r}: {e}") from e

    if proc.returncode != 0:
        err = proc.stderr.strip() or f"frontend exited with code {proc.returncode}"
        raise FrontendError(err)

    raw = proc.stdout.strip()
    if not raw:
        raise FrontendError("frontend produced no output (expected JSON AST on stdout)")

    try:
        ast = json.loads(raw)
    except json.JSONDecodeError as e:
        raise FrontendError(f"frontend produced invalid JSON: {e}") from e

    try:
        validate(ast)
    except ASTError as e:
        raise FrontendError(str(e)) from e

    return ast