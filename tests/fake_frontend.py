#!/usr/bin/env python3
"""Fake frontend used only by tests: emits a fixed AST."""

import json
import sys

AST = {
    "ast_version": "1",
    "root": {
        "type": "Call",
        "fn": "env",
        "kwargs": {
            "languages": {"type": "List", "items": [{"type": "Str", "value": "nodejs"}]},
            "packages": {"type": "List", "items": [{"type": "Str", "value": "git"}]},
        },
    },
}

if __name__ == "__main__":
    json.dump(AST, sys.stdout)