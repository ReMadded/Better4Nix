"""Render the JSON AST (schemas/ast-v1.json) into Nix source code."""

from __future__ import annotations

from typing import Any

INDENT = "  "


class NixRenderError(Exception):
    pass


def render(node: Any, indent: int = 0) -> str:
    if not isinstance(node, dict):
        raise NixRenderError("node must be a dict")
    t = node.get("type")
    pad = INDENT * indent

    # Special case: env(...) becomes a real shell.nix, not `env { ... }`.
    if t == "Call" and node.get("fn") == "env":
        return render_env(node.get("kwargs", {}))

    if t == "AttrSet":
        entries = node["entries"]
        if not entries:
            return "{ }"
        lines = ["{"]
        for e in entries:
            key = _render_key(e["key"])
            val = render(e["value"], indent + 1)
            lines.append(f"{INDENT * (indent + 1)}{key} = {val};")
        lines.append(f"{pad}}}")
        return "\n".join(lines)

    if t == "List":
        items = node["items"]
        if not items:
            return "[ ]"
        inner = " ".join(render(i, indent) for i in items)
        return f"[ {inner} ]"

    if t == "Str":
        return _nix_string(node["value"])

    if t == "Int":
        return str(node["value"])

    if t == "Bool":
        return "true" if node["value"] else "false"

    if t == "Null":
        return "null"

    if t == "Ident":
        return node["name"]

    if t == "Call":
        fn = node["fn"]
        args = [render(a, indent) for a in node.get("args", [])]
        kwargs = node.get("kwargs", {})
        parts = list(args)
        for k, v in kwargs.items():
            parts.append(f"{k} = {render(v, indent)}")
        if not parts:
            return fn
        return f"{fn} {{ {'; '.join(parts)} }}"

    if t == "Let":
        lines = ["let"]
        for b in node["bindings"]:
            lines.append(f"{INDENT}{b['name']} = {render(b['value'], indent + 1)};")
        lines.append("in")
        lines.append(render(node["body"], indent))
        return "\n".join(lines)

    if t == "With":
        scope = render(node["scope"], indent)
        body = render(node["body"], indent)
        return f"with {scope};\n{pad}{body}"

    if t == "Select":
        base = render(node["base"], indent)
        return base + "".join(f".{p}" for p in node["path"])

    raise NixRenderError(f"cannot render node type {t!r}")


def render_env(kwargs: dict) -> str:
    """Turn `env(...)` kwargs into a complete shell.nix source."""
    languages = _str_list(kwargs.get("languages"))
    packages = _str_list(kwargs.get("packages"))
    from_nur = _str_list(kwargs.get("from_nur"))
    shell_hook = kwargs.get("shell_hook")
    hook_value = shell_hook["value"] if shell_hook and shell_hook.get("type") == "Str" else None

    pkg_attrs = languages + packages
    nur_attrs = [f"nur.{p}" for p in from_nur]

    header = "{ pkgs ? import <nixpkgs> {} }:\n"

    if from_nur:
        nur_url = "https://github.com/nix-community/NUR/archive/master.tar.gz"
        prelude = (
            "let\n"
            f'  nur = import (builtins.fetchTarball "{nur_url}") {{ inherit pkgs; }};\n'
            "in\n"
        )
    else:
        prelude = ""

    body_lines = ["pkgs.mkShell {"]
    if pkg_attrs or nur_attrs:
        body_lines.append(f"{INDENT}buildInputs = with pkgs; [")
        for p in pkg_attrs:
            body_lines.append(f"{INDENT * 2}{p}")
        for p in nur_attrs:
            body_lines.append(f"{INDENT * 2}{p}")
        body_lines.append(f"{INDENT}];")
    if hook_value:
        body_lines.append(f"{INDENT}shellHook = {_nix_string(hook_value)};")
    body_lines.append("}")

    return header + prelude + "\n".join(body_lines)


def _str_list(node: Any) -> list[str]:
    if node is None:
        return []
    if node.get("type") != "List":
        raise NixRenderError("expected a List")
    out: list[str] = []
    for item in node["items"]:
        if item.get("type") != "Str":
            raise NixRenderError("expected a list of strings")
        out.append(item["value"])
    return out


def _render_key(key: str) -> str:
    if key.replace("_", "").replace("-", "").isalnum() and not key[0].isdigit():
        return key
    return _nix_string(key)


def _nix_string(s: str) -> str:
    escaped = s.replace("\\", "\\\\").replace('"', '\\"').replace("${", "\\${")
    return f'"{escaped}"'