# Issue workflow

As of 2026-11-11, the team uses one shared `dev` branch for all task work. The branch is based on the latest phase merge to `main`. Each teammate creates a short-lived task branch from current `dev` and opens a PR back to `dev`. Task PRs need no teammate approval; required CI checks and resolved conversations still apply.

After all nine tasks and the shared acceptance gate for a phase are verified, open a PR from `dev` to protected `main`. That phase integration PR needs one current approval from a named teammate other than its author, all required CI checks, resolved conversations, and an up-to-date base. Do not push directly to `main`.

The phase and task issue links are in [the backlog](ISSUE_BACKLOG.md). [Dependencies and merge order](DEPENDENCIES_AND_MERGE_ORDER.md) explain task ordering. Inspect native issue blockers before starting planned work; issue relationships do not replace evidence or CI.

Use `feat/P05-S1-short-description`, `fix/…`, or `chore/…` for task branches. Link the task issue in the PR. Use `Refs #N` for partial work; close an issue only after its work and evidence are complete and merged to `dev`. Keep each owner's handoff current. Keep the phase parent open until all nine tasks and its shared gate are verified.
