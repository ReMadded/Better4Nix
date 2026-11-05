import json
import subprocess
import sys
import tempfile
import os
from pathlib import Path

MAIN = Path(__file__).parent.parent / "better4nix_frontend_python" / "main.py"


def run(src: str) -> tuple[int, dict, dict]:
    fd, path = tempfile.mkstemp(suffix=".py")
    os.close(fd)
    Path(path).write_text(src)
    try:
        proc = subprocess.run(
            [sys.executable, str(MAIN), path],
            capture_output=True, text=True,
        )
    finally:
        os.unlink(path)
    out = json.loads(proc.stdout) if proc.stdout.strip() else {}
    err = json.loads(proc.stderr) if proc.stderr.strip() and proc.returncode != 0 else {}
    return proc.returncode, out, err


def test_env_with_lists():
    rc, out, _ = run('env(languages=["nodejs", "go"], packages=["git"])\n')
    assert rc == 0
    root = out["root"]
    assert root["type"] == "Call"
    assert root["fn"] == "env"
    assert root["kwargs"]["languages"]["type"] == "List"
    assert root["kwargs"]["languages"]["items"][0] == {"type": "Str", "value": "nodejs"}


def test_dict_becomes_attrset():
    rc, out, _ = run('env(vars={"a": 1, "b": True, "c": None})\n')
    assert rc == 0
    vs = out["root"]["kwargs"]["vars"]
    assert vs["type"] == "AttrSet"
    assert [e["key"] for e in vs["entries"]] == ["a", "b", "c"]


def test_forbidden_class():
    rc, out, err = run('class X: pass\nenv()\n')
    assert rc != 0
    assert "unsupported" in err["error"].lower() or "exactly one" in err["error"].lower()


def test_forbidden_for_loop():
    rc, _, err = run('env(packages=[x for x in []])\n')
    assert rc != 0
    assert "line" in err


def test_forbidden_unknown_call():
    rc, _, err = run('print("hi")\n')
    assert rc != 0
    assert "not allowed" in err["error"]