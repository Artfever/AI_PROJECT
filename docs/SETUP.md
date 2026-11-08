# Editable installation and portable paths

Use Python **3.12** for local development and deployment. The team confirmed
this version for P01-A1; `pyproject.toml` enforces `>=3.12,<3.13`, and CI uses
3.12. A newer system default does not select the project's supported version.

From a fresh terminal, change to your clone's root (the directory containing
`pyproject.toml`). The clone may have any name, including a path with spaces.

## Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv/Scripts/python.exe --version
.venv/Scripts/python.exe -m pip install -e ".[dev]"
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m streamlit run app/Home.py
```

If the launcher cannot find Python 3.12, install that interpreter first. If you
already use uv, `uv venv --python 3.12 --seed .venv` is an alternative environment
creation command; the remaining commands are unchanged. Explicit environment
paths avoid activation-policy and PATH differences between terminals.

## Linux or macOS shell

```sh
python3.12 -m venv .venv
.venv/bin/python --version
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m streamlit run app/Home.py
```

The `[dev]` extra installs pytest and Ruff along with the application dependency.
The editable install makes `fleetpulse` importable from this clone without
`PYTHONPATH` or `sys.path` edits. Reinstall after moving the clone or changing
dependency/package metadata. The environment belongs to one clone; do not copy
it to another laptop or location.

## Check the setup

Run the small configuration checks independently of the Streamlit UI test:

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_bootstrap.py -k "project_paths or installed_package_paths"
```

On Linux/macOS, replace `.venv/Scripts/python.exe` with `.venv/bin/python`.
The checks verify the project metadata and Home entrypoint exist, and launch a
fresh Python process from a temporary directory with `PYTHONPATH` removed.
That process must import the installed `fleetpulse` package and resolve the same
repository root. If the import fails, run the editable install using the same
environment's interpreter. No dataset, trained artifact, or path edit is needed.
The full `python -m pytest -q` command above also exercises Home's empty state.

## File-location contract

Import `PROJECT_ROOT` from `fleetpulse`. It derives the clone root from the
installed source file, independently of the process's working directory:

```python
from fleetpulse import PROJECT_ROOT

raw_directory = PROJECT_ROOT / "data" / "raw"
artifact_directory = PROJECT_ROOT / "artifacts"
home_file = PROJECT_ROOT / "app" / "Home.py"
```

These are filesystem locations, not loaded datasets or model artifacts. Paths
use `pathlib.Path`; consumers should join segments rather than embedding a
developer's absolute path. `PROJECT_ROOT` is the source-checkout contract for an
editable installation, not a promise that a standalone wheel contains app,
data, or docs directories. Relative CLI arguments such as `app/Home.py` still
require running the command from the clone root.

`.gitignore` excludes the virtual environment, caches, build metadata, local
private guides, and data/artifact contents. Tracked `.gitkeep` markers preserve
the [empty scaffold](REPOSITORY_LAYOUT.md); they do not provide data or models.

## Deployment compatibility

Checked 9 November 2026: Streamlit's [Community Cloud deployment documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
lists Python 3.12 as supported and selectable in Advanced settings. Select 3.12
explicitly when deployment is implemented. This confirms the interpreter choice,
not a deployed app or compatibility of future model dependencies.

The current build uses setuptools. Community Cloud's [dependency documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)
routes a bare `pyproject.toml` to Poetry, so the deployment owner must explicitly
validate the package-install route when preparing P07 deployment. The local
editable-install instructions above do not establish cloud deployment readiness.
