from better4nix.backend.nix_be import render


def test_attrset_simple():
    ast = {"type": "AttrSet", "entries": [{"key": "a", "value": {"type": "Int", "value": 1}}]}
    assert render(ast) == "{\n  a = 1;\n}"


def test_list_of_strings():
    ast = {"type": "List", "items": [
        {"type": "Str", "value": "git"},
        {"type": "Str", "value": "jq"},
    ]}
    assert render(ast) == '[ "git" "jq" ]'


def test_string_escaping():
    ast = {"type": "Str", "value": 'a"b${c}'}
    assert render(ast) == '"a\\"b\\${c}"'


def test_bool_and_null():
    assert render({"type": "Bool", "value": True}) == "true"
    assert render({"type": "Bool", "value": False}) == "false"
    assert render({"type": "Null"}) == "null"


def test_select_and_ident():
    ast = {"type": "Select", "base": {"type": "Ident", "name": "pkgs"}, "path": ["git"]}
    assert render(ast) == "pkgs.git"


def test_let():
    ast = {
        "type": "Let",
        "bindings": [{"name": "x", "value": {"type": "Int", "value": 1}}],
        "body": {"type": "Ident", "name": "x"},
    }
    assert render(ast) == "let\n  x = 1;\nin\nx"


def _env_ast(**kwargs):
    return {
        "type": "Call",
        "fn": "env",
        "kwargs": kwargs,
    }


def test_env_minimal():
    ast = _env_ast(
        packages={"type": "List", "items": [{"type": "Str", "value": "git"}]},
    )
    out = render(ast)
    assert out.startswith("{ pkgs ? import <nixpkgs> {} }:")
    assert "pkgs.mkShell {" in out
    assert "buildInputs = with pkgs; [" in out
    assert "git" in out
    assert out.rstrip().endswith("}")


def test_env_languages_and_packages_merge():
    ast = _env_ast(
        languages={"type": "List", "items": [
            {"type": "Str", "value": "nodejs"},
            {"type": "Str", "value": "go"},
        ]},
        packages={"type": "List", "items": [{"type": "Str", "value": "git"}]},
    )
    out = render(ast)
    idx_node = out.index("nodejs")
    idx_go = out.index("go")
    idx_git = out.index("git")
    assert idx_node < idx_go < idx_git


def test_env_from_nur_adds_let():
    ast = _env_ast(
        packages={"type": "List", "items": [{"type": "Str", "value": "git"}]},
        from_nur={"type": "List", "items": [
            {"type": "Str", "value": "repos.mic92.hello"},
        ]},
    )
    out = render(ast)
    assert "let" in out
    assert "nur = import (builtins.fetchTarball" in out
    assert "nur.repos.mic92.hello" in out
    assert "inherit pkgs" in out


def test_env_shell_hook():
    ast = _env_ast(
        packages={"type": "List", "items": [{"type": "Str", "value": "git"}]},
        shell_hook={"type": "Str", "value": "echo ready"},
    )
    out = render(ast)
    assert 'shellHook = "echo ready";' in out