"""Command-line interface: `better4nix build <file>`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .backend.nix_be import NixRenderError, render
from .discovery import find_frontend
from .runner import FrontendError, run_frontend


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="better4nix")
    sub = parser.add_subparsers(dest="cmd", required=True)

    build = sub.add_parser("build", help="compile a config file to Nix")
    build.add_argument("source", type=Path, help="input config file")
    build.add_argument("-o", "--output", type=Path, default=None, help="output .nix path")
    build.add_argument("--stdout", action="store_true", help="print Nix to stdout")

    args = parser.parse_args(argv)

    if args.cmd == "build":
        return _cmd_build(args)
    return 1


def _cmd_build(args) -> int:
    src: Path = args.source
    if not src.exists():
        print(f"better4nix: file not found: {src}", file=sys.stderr)
        return 2

    ext = src.suffix
    exe = find_frontend(ext)
    if exe is None:
        print(
            f"better4nix: no frontend installed for {ext!r}.\n"
            f"Install a frontend, e.g. `better4nix-frontend-{ext.lstrip('.')}` on PATH.",
            file=sys.stderr,
        )
        return 2

    try:
        ast = run_frontend(exe, src)
    except FrontendError as e:
        print(f"better4nix: frontend error: {e}", file=sys.stderr)
        return 3

    try:
        nix = render(ast["root"])
    except NixRenderError as e:
        print(f"better4nix: render error: {e}", file=sys.stderr)
        return 4

    if args.stdout:
        print(nix)
        return 0

    out: Path = args.output or src.with_suffix(".nix")
    out.write_text(nix + "\n", encoding="utf-8")
    print(f"generated {out}")
    print(f"run: nix-shell {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())