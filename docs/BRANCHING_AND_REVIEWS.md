# Branches, Issues, and reviews

`main` is the only long-lived branch and the production source. A GitHub Issue records agreed work, ownership, and acceptance criteria. It does not change code. Use a short-lived descriptive branch from current `main`, then open a PR to `main`. Link any relevant issue; use `Closes #N` only when merging the PR completes it. Squash-merge ordinary work and delete its short-lived branch afterward.

Every PR, including tooling, documentation, and release changes, requires one actual approving review from another teammate with write access:

| Author | Either eligible reviewer |
| --- | --- |
| Shaheer (`Artfever`) | Abdullah (`Abdullah-SE-bit`) or Taha (`TahaSohail-Goat`) |
| Abdullah (`Abdullah-SE-bit`) | Shaheer (`Artfever`) or Taha (`TahaSohail-Goat`) |
| Taha (`TahaSohail-Goat`) | Shaheer (`Artfever`) or Abdullah (`Abdullah-SE-bit`) |

Comments and review requests are not approvals. GitHub's native one-review rule applies; stale approvals are dismissed, the latest reviewable push needs another person's approval, conversations must be resolved, and required CI must pass. The owner can still change repository settings administratively. Do not push directly to protected `main` or bypass a review for setup work.

The `branch-policy` CI job checks that PRs target `main` and originate from a branch in this repository. When working on a planned task, inspect its native task and predecessor-phase blockers before proceeding. The full process and source issue map are in [the backlog](ISSUE_BACKLOG.md) and [dependency guide](DEPENDENCIES_AND_MERGE_ORDER.md).
