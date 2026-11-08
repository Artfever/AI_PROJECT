# Contributing

Use Python 3.12. Create a virtual environment, run `python -m pip install -e ".[dev]"`, then `python -m pytest -q` and `ruff check .`. Start the preview with `streamlit run app/Home.py`.

Use an assigned, ready GitHub Issue for agreed work; describe the outcome and what will count as done. Do not create speculative Issues just to fill a list. Create `feat/<task-id>-<short-description>`, `fix/<task-id>-<short-description>`, or `chore/<task-id>-<short-description>` from current `main` (for example `feat/P05-S1-rolling-features`). Open a PR back to `main` and link its Issue, for example with `Closes #12` only when the PR fully resolves it; use `Refs #12` for partial work. One teammate other than the author must approve the current revision. Use the PR template and include actual test results. Never commit raw datasets, local plans, or trained artifacts without an explicit reviewed artifact policy.
