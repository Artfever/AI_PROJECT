import os
import subprocess
import sys
from pathlib import Path

from fleetpulse import PROJECT_ROOT


def test_project_paths_and_entrypoint():
    assert (PROJECT_ROOT / "pyproject.toml").is_file()
    assert (PROJECT_ROOT / "app" / "Home.py").is_file()


def test_installed_package_paths_from_another_directory(tmp_path):
    """Catch imports or repository paths that accidentally depend on the shell CWD."""
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from fleetpulse import PROJECT_ROOT; print(PROJECT_ROOT)",
        ],
        cwd=tmp_path,
        env=environment,
        text=True,
        capture_output=True,
        check=True,
    )
    resolved_root = Path(result.stdout.strip())
    assert resolved_root == PROJECT_ROOT
    assert (resolved_root / "pyproject.toml").is_file()
    assert (resolved_root / "app" / "Home.py").is_file()


def test_home_empty_state():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(PROJECT_ROOT / "app" / "Home.py")).run()
    assert not app.exception
    assert any("no data, trained models" in item.value for item in app.info)
