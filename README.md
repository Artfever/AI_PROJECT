# FleetPulse AI

FleetPulse is a planned Streamlit application for simulated turbofan remaining-useful-life prediction and maintenance scheduling. The repository is in its bootstrap stage; no trained model or final evaluation is available yet.

Use Python 3.12. Run `python -m pip install -e ".[dev]"`, `python -m pytest -q`, and `streamlit run app/Home.py` for the current preview.

Follow the [editable-install guide](docs/SETUP.md) to select Python 3.12, create an isolated environment on Windows/Linux/macOS, and use repository-relative file paths.

The [shared repository layout](docs/REPOSITORY_LAYOUT.md) describes the package folders and the empty data/artifact directories preserved in a fresh clone.

`main` is the only long-lived branch. Track agreed work in GitHub Issues, make changes on a short-lived branch from `main`, and open a pull request back to `main`. One other named teammate must approve after CI passes. Start with [repository agent instructions](AGENTS.md) and the current owner's handoff ([Shaheer](handoff_Shaheer.md), [Abdullah](handoff_Abdullah.md), or [Taha](handoff_Taha.md)). See [the issue backlog](docs/ISSUE_BACKLOG.md), [dependencies and merge order](docs/DEPENDENCIES_AND_MERGE_ORDER.md), [workflow migration](docs/ISSUE_WORKFLOW_MIGRATION.md), [contributing](docs/CONTRIBUTING.md), [branching and reviews](docs/BRANCHING_AND_REVIEWS.md), [CI and delivery](docs/CI_CD.md), [capability inventory](docs/CI_CAPABILITIES.md), and [course evidence](docs/COURSE_COMPLIANCE.md).
