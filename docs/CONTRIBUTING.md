# Contributing

Use Python 3.12. Create a virtual environment, run `python -m pip install -e ".[dev]"`, then `python -m pytest -q` and `ruff check .`. Start the preview with `streamlit run app/Home.py`.

Use the platform-specific commands and path contract in the [editable-install guide](SETUP.md). Run commands with that environment's interpreter; the system default may use an unsupported Python version.

For planned work, use an assigned, ready GitHub Issue; describe the outcome and what will count as done. Do not create speculative Issues just to fill a list. Create a short-lived descriptive branch from current `main`. Open a PR back to `main` and link a relevant issue when one exists, for example with `Closes #12` only when the PR fully resolves it; use `Refs #12` for partial work. One teammate other than the author must approve the current revision. Use the PR template and include actual test results. Never commit raw datasets, local plans, or trained artifacts without an explicit reviewed artifact policy.

Read the root [AGENTS.md](../AGENTS.md) and your `handoff_<Name>.md` before starting a new session. The master plan and personal guides are intentionally ignored; obtain a local copy from the team if needed. The assigned issue and checked-in backlog manifest remain available in a fresh clone.
