# Issue workflow migration

The current route is a GitHub task issue, a short-lived branch from `main`, and a pull request back to protected `main`. One other named teammate approves the latest revision: for Shaheer, Abdullah or Taha; for Abdullah, Shaheer or Taha; for Taha, Abdullah or Shaheer. Required CI and resolved conversations also apply. A review request, comment, bot review, or the author's own review does not count.

This supersedes the earlier `dev` integration route and two-teammate approval wording. The former `dev` branch had no unique commits and was deleted during the previous repository setup at the owner's request. Existing historical PRs, commits, and reviews remain in GitHub. Do not infer implementation completion from the new backlog; issue status follows actual evidence.

The phase and task issue links are in [the backlog](ISSUE_BACKLOG.md). [Dependencies and merge order](DEPENDENCIES_AND_MERGE_ORDER.md) explain when downstream work can merge. Native issue relationships are for planning; required CI and branch protection decide whether a PR can merge.

For a numbered task, use `feat/P05-S1-short-description`, `fix/…`, or `chore/…`. Link the task issue in the PR. Use `Closes #N` only if the PR fully completes it; use `Refs #N` for partial work. Keep each owner's handoff file current with evidence and next consumers. A phase parent remains open until all nine tasks and its shared gate are verified.
