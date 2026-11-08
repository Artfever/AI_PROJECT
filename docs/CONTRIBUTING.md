# Contributing

Use Python 3.12. Create a virtual environment, run `python -m pip install -e ".[dev]"`, then `python -m pytest -q` and `ruff check .`. Start the preview with `streamlit run app/Home.py`.

Create `feat/<person>/<task>`, `fix/<person>/<task>`, or `chore/<person>/<task>` from `dev`. Open a PR to `dev`; both other teammates must approve the current revision. Use the PR template and include actual test results. Never commit raw datasets, local plans, or trained artifacts without an explicit reviewed artifact policy.
