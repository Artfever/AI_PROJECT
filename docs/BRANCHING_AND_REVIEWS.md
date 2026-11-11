# Branches, issues, and reviews

`dev` is the shared integration branch for Shaheer, Abdullah, and Taha. `main` is the protected phase-release branch. A GitHub Issue records agreed work, ownership, dependencies, and acceptance criteria; it does not change code.

For an assigned task, branch from current `dev` using a short descriptive name such as `feat/P05-S1-description`, then open a PR back to `dev`. Link the task issue. Task PRs do not require teammate approval; required CI and resolved review conversations still apply. Use `Refs #N` for partial work, and close an issue only when its evidence is complete and its change is merged into `dev`.

All five required checks apply on `dev`: `branch-policy`, `quality`, `unit-and-contract-tests`, `streamlit-smoke`, and `ci-gate`. Inspect native issue blockers before planned work and verify producer outputs before consumers rely on them. Do not push straight to `main`.

After all nine tasks and the shared gate for a phase are verified, open one integration PR from `dev` to protected `main`. That PR requires one current approval from a teammate other than its author:

| Author | Either eligible reviewer |
| --- | --- |
| Shaheer (`Artfever`) | Abdullah (`Abdullah-SE-bit`) or Taha (`TahaSohail-Goat`) |
| Abdullah (`Abdullah-SE-bit`) | Shaheer (`Artfever`) or Taha (`TahaSohail-Goat`) |
| Taha (`TahaSohail-Goat`) | Shaheer (`Artfever`) or Abdullah (`Abdullah-SE-bit`) |

The phase PR also requires all five checks, resolved conversations, and an up-to-date `dev`. Comments, review requests, bot reviews, and the author's own review do not count. Keep `main` protection intact; do not bypass it. The owner can change repository settings administratively.

See the [issue backlog](ISSUE_BACKLOG.md) and [dependency guide](DEPENDENCIES_AND_MERGE_ORDER.md) for task allocation and phase ordering.
