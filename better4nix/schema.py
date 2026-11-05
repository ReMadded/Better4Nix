"""Validation of the JSON AST against schemas/ast-v1.json (no external deps)."""

from __future__ import annotations

from typing import Any

SUPPORTED_AST_VERSION = "1"


class ASTError(Exception):
    """Raised when the AST is invalid or uses an unsupported version."""


def _fail(path: str, msg: str) -> None:
    raise ASTError(f"AST error at {path or '<root>'}: {msg}")


def validate(ast: Any) -> None:
    """Validate the top-level AST envelope and recursively validate root node."""
    if not isinstance(ast, dict):
        _fail("", "top-level AST must be an object")
    if "ast_version" not in ast:
        _fail("", "missing required field 'ast_version'")
    if ast["ast_version"] != SUPPORTED_AST_VERSION:
        _fail(
            "ast_version",
            f"plugin uses ast_version={ast['ast_version']!r}, "
            f"but this core supports only {SUPPORTED_AST_VERSION!r}. "
            f"Update the core (pip install -U better4nix) or downgrade the plugin.",
        )
    if "root" not in ast:
        _fail("", "missing required field 'root'")
    _validate_node(ast["root"], "root")


def _validate_node(node: Any, path: str) -> None:
    if not isinstance(node, dict):
        _fail(path, "node must be an object")
    t = node.get("type")
    if t is None:
        _fail(path, "node is missing 'type'")

    if t == "AttrSet":
        entries = node.get("entries")
        if not isinstance(entries, list):
            _fail(path, "'entries' must be a list")
        for i, e in enumerate(entries):
            if not isinstance(e, dict) or "key" not in e or "value" not in e:
                _fail(f"{path}.entries[{i}]", "entry must have 'key' and 'value'")
            if not isinstance(e["key"], str):
                _fail(f"{path}.entries[{i}].key", "key must be a string")
            _validate_node(e["value"], f"{path}.entries[{i}].value")

    elif t == "List":
        items = node.get("items")
        if not isinstance(items, list):
            _fail(path, "'items' must be a list")
        for i, item in enumerate(items):
            _validate_node(item, f"{path}.items[{i}]")

    elif t == "Str":
        if not isinstance(node.get("value"), str):
            _fail(path, "'value' must be a string")

    elif t == "Int":
        if not isinstance(node.get("value"), int) or isinstance(node.get("value"), bool):
            _fail(path, "'value' must be an integer")

    elif t == "Bool":
        if not isinstance(node.get("value"), bool):
            _fail(path, "'value' must be a boolean")

    elif t == "Null":
        pass

    elif t == "Ident":
        if not isinstance(node.get("name"), str):
            _fail(path, "'name' must be a string")

    elif t == "Call":
        if not isinstance(node.get("fn"), str):
            _fail(path, "'fn' must be a string")
        args = node.get("args", [])
        if not isinstance(args, list):
            _fail(path, "'args' must be a list")
        for i, a in enumerate(args):
            _validate_node(a, f"{path}.args[{i}]")
        kwargs = node.get("kwargs", {})
        if not isinstance(kwargs, dict):
            _fail(path, "'kwargs' must be an object")
        for k, v in kwargs.items():
            _validate_node(v, f"{path}.kwargs.{k}")

    elif t == "Let":
        bindings = node.get("bindings")
        if not isinstance(bindings, list):
            _fail(path, "'bindings' must be a list")
        for i, b in enumerate(bindings):
            if not isinstance(b, dict) or "name" not in b or "value" not in b:
                _fail(f"{path}.bindings[{i}]", "binding must have 'name' and 'value'")
            if not isinstance(b["name"], str):
                _fail(f"{path}.bindings[{i}].name", "name must be a string")
            _validate_node(b["value"], f"{path}.bindings[{i}].value")
        _validate_node(node.get("body"), f"{path}.body")

    elif t == "With":
        _validate_node(node.get("scope"), f"{path}.scope")
        _validate_node(node.get("body"), f"{path}.body")

    elif t == "Select":
        _validate_node(node.get("base"), f"{path}.base")
        path_list = node.get("path")
        if not isinstance(path_list, list) or not all(isinstance(p, str) for p in path_list):
            _fail(path, "'path' must be a list of strings")

    else:
        _fail(path, f"unknown node type {t!r}")