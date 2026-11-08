# Contributing

Use Python 3.12. Create a virtual environment, run `python -m pip install -e ".[dev]"`, then `python -m pytest -q` and `ruff check .`. Start the preview with `streamlit run app/Home.py`.

Use a GitHub Issue for agreed work; describe the outcome and what will count as done. Do not create speculative Issues just to fill a list. Create `feat/<person>/<task>`, `fix/<person>/<task>`, or `chore/<person>/<task>` from `main`. Open a PR back to `main` and link its Issue, for example with `Closes #12` when the PR fully resolves it. One teammate other than the author must approve the current revision. Use the PR template and include actual test results. Never commit raw datasets, local plans, or trained artifacts without an explicit reviewed artifact policy.
