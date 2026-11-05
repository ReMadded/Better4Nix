"""Python -> Better4Nix JSON AST (ast-v1) frontend."""

from __future__ import annotations

import ast
import json
import sys

AST_VERSION = "1"
ALLOWED_CALLS = {"env", "let", "with_"}


class UnsupportedConstruct(Exception):
    def __init__(self, msg: str, lineno: int | None = None) -> None:
        super().__init__(msg)
        self.msg = msg
        self.lineno = lineno


def parse_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as e:
        raise UnsupportedConstruct(f"python syntax error: {e.msg}", e.lineno) from e
    return convert_module(tree)


def convert_module(tree: ast.Module) -> dict:
    if len(tree.body) != 1:
        first = tree.body[0] if tree.body else None
        raise UnsupportedConstruct(
            "config file must contain exactly one top-level `env(...)` call",
            first.lineno if first else None,
        )
    stmt = tree.body[0]
    if not isinstance(stmt, ast.Expr):
        raise UnsupportedConstruct(
            "top-level statement must be an expression: `env(...)`",
            stmt.lineno,
        )
    return {"ast_version": AST_VERSION, "root": convert_expr(stmt.value)}


def convert_expr(node: ast.AST) -> dict:
    if isinstance(node, ast.Call):
        return convert_call(node)
    if isinstance(node, ast.Dict):
        return convert_dict(node)
    if isinstance(node, ast.List):
        return convert_list(node)
    if isinstance(node, ast.Constant):
        return convert_constant(node)
    if isinstance(node, ast.Name):
        return {"type": "Ident", "name": node.id}
    if isinstance(node, ast.Attribute):
        return {
            "type": "Select",
            "base": convert_expr(node.value),
            "path": [node.attr],
        }
    raise UnsupportedConstruct(
        f"unsupported Python construct: {type(node).__name__}",
        getattr(node, "lineno", None),
    )


def convert_call(node: ast.Call) -> dict:
    if not isinstance(node.func, ast.Name):
        raise UnsupportedConstruct(
            "only simple calls like `env(...)`, `let(...)`, `with_(...)` are allowed",
            node.lineno,
        )
    name = node.func.id
    if name not in ALLOWED_CALLS:
        raise UnsupportedConstruct(
            f"call to {name!r} is not allowed; allowed: {sorted(ALLOWED_CALLS)}",
            node.lineno,
        )
    args = [convert_expr(a) for a in node.args]
    kwargs: dict[str, dict] = {}
    for kw in node.keywords:
        if kw.arg is None:
            raise UnsupportedConstruct("`**kwargs` is not allowed", node.lineno)
        kwargs[kw.arg] = convert_expr(kw.value)
    out: dict = {"type": "Call", "fn": name, "args": args}
    if kwargs:
        out["kwargs"] = kwargs
    return out


def convert_dict(node: ast.Dict) -> dict:
    entries: list[dict] = []
    for k, v in zip(node.keys, node.values):
        if k is None:
            raise UnsupportedConstruct("`**spread` in dict is not allowed", node.lineno)
        if not isinstance(k, ast.Constant) or not isinstance(k.value, str):
            raise UnsupportedConstruct("dict keys must be string literals", getattr(k, "lineno", node.lineno))
        entries.append({"key": k.value, "value": convert_expr(v)})
    return {"type": "AttrSet", "entries": entries}


def convert_list(node: ast.List) -> dict:
    return {"type": "List", "items": [convert_expr(e) for e in node.elts]}


def convert_constant(node: ast.Constant) -> dict:
    v = node.value
    if isinstance(v, bool):
        return {"type": "Bool", "value": v}
    if isinstance(v, int):
        return {"type": "Int", "value": v}
    if isinstance(v, str):
        return {"type": "Str", "value": v}
    if v is None:
        return {"type": "Null"}
    raise UnsupportedConstruct(f"unsupported literal: {v!r}", node.lineno)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: better4nix-frontend-py <config.py>", file=sys.stderr)
        return 2
    try:
        ast_dict = parse_file(sys.argv[1])
    except UnsupportedConstruct as e:
        err = {"error": e.msg}
        if e.lineno is not None:
            err["line"] = e.lineno
        print(json.dumps(err), file=sys.stderr)
        return 1
    except OSError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 1
    json.dump(ast_dict, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())