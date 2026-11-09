# FleetPulse repository instructions

Apply these instructions throughout this repository. Read the current user request first. On a new session, inspect `git status`, the current branch, any relevant GitHub issue and its native blockers, and the owner's `handoff_<Name>.md` before editing. Preserve uncommitted work and teammate changes.

## Sources and scope

- `main` is the only long-lived branch. The [issue backlog](docs/ISSUE_BACKLOG.md), [dependency guide](docs/DEPENDENCIES_AND_MERGE_ORDER.md), and `planning/backlog.json` record the 26-phase task allocation. The assigned issue supplies the immediate requirement and acceptance criteria. Actual code, tests, and reviewed artifacts determine what is complete.
- `FleetPulse_Phase_Implementation_Plan.md`, `Shaheer.md`, `Abdullah.md`, and `Taha.md` are intentionally ignored local planning files. A fresh clone will not contain them. Read a local copy when supplied; use the published issue and manifest if it is absent. Never add those files to a commit.
- Work on one agreed task at a time; inspect relevant issue blockers before starting numbered backlog work. Do not silently implement another owner's subsystem or claim missing data, trained models, metrics, deployment, or human checks. Preserve the software-only NASA C-MAPSS FD001 scope and the scientific rules in the issue and [course evidence note](docs/COURSE_COMPLIANCE.md).

## Branch, review, and checks

- Start a short-lived descriptive branch from current `main`. Open a PR back to protected `main` and link any relevant issue. Use `Closes #N` only for full completion; use `Refs #N` for partial work. Do not use `dev` or push directly to `main`.
- One actual approving review from **one other named teammate** is required: Shaheer's PR may be approved by Abdullah or Taha; Abdullah's by Shaheer or Taha; Taha's by Shaheer or Abdullah. Required CI, current review after changes, and resolved conversations also apply. Respect relevant native hard blockers for planned backlog work. A comment, bot review, or review request is not an approval. See [branching and reviews](docs/BRANCHING_AND_REVIEWS.md).
- Run checks relevant to the changed behavior and report exact commands and outcomes. The baseline commands are `ruff check .`, `python -m pytest -q`, and, for app changes, `streamlit run app/Home.py`. Record any check that could not run as **NOT RUN** with its reason. Do not create trivial tests solely to mirror an implementation.

## Handoffs

- Maintain `handoff_Shaheer.md`, `handoff_Abdullah.md`, or `handoff_Taha.md` for the task owner. Record the current phase/task, verified work with evidence, changed files, tests and actual results, blockers, teammate dependencies, relevant commits and PR links, and exact next steps. Distinguish planned work from completion.
- Read the handoff at session start. Update it before each work commit and after a PR is opened, updated, or merged. Put a completed commit hash in the next substantive update; do not make an endless sequence of commits solely to record their own hashes.
- Do not send teammate messages or claim their approval unless the user explicitly authorizes that action. Report human checks and decisions that remain.
