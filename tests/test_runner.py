import sys
from pathlib import Path

import pytest

from better4nix.runner import FrontendError, run_frontend


FAKE = Path(__file__).parent / "fake_frontend.py"


def test_run_frontend_ok(tmp_path: Path):
    src = tmp_path / "config.py"
    src.write_text("env()\n")
    ast = run_frontend(sys.executable, str(FAKE))
    assert ast["ast_version"] == "1"
    assert ast["root"]["type"] == "Call"


def test_run_frontend_invalid_json(tmp_path: Path):
    fake = tmp_path / "bad.sh"
    fake.write_text("#!/bin/sh\necho 'not json'\n")
    fake.chmod(0o755)
    with pytest.raises(FrontendError):
        run_frontend(str(fake), str(tmp_path / "x.py"))


def test_run_frontend_bad_version(tmp_path: Path):
    fake = tmp_path / "badver.sh"
    fake.write_text(
        "#!/bin/sh\n"
        "echo '{\"ast_version\":\"99\",\"root\":{\"type\":\"Null\"}}'\n"
    )
    fake.chmod(0o755)
    with pytest.raises(FrontendError) as ei:
        run_frontend(str(fake), str(tmp_path / "x.py"))
    assert "ast_version" in str(ei.value)