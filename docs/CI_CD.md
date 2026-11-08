# CI and delivery

Development CI runs on PRs to `main`, pushes to `main`, and manual dispatch. The required check names are `branch-policy`, `quality`, `unit-and-contract-tests`, `streamlit-smoke`, and `ci-gate`.

The test job uploads `reports/junit.xml` even on failure. The gate writes a job summary with each dependency result. The smoke job starts `app/Home.py`, probes `/_stcore/health`, captures the log on failure, and stops the process. PR code runs with read-only workflow permissions.

`main` requires a PR, one approving teammate review, dismissal of stale approvals, approval after the latest reviewable push, resolved conversations, and all five CI checks with the branch up to date. Force pushes and deletion are disabled, and the protection applies to administrators. Verify the effective settings with `gh api repos/Artfever/AI_PROJECT/branches/main/protection`. The owner can still change repository settings.

Streamlit Community Cloud should be configured for this repository, branch `main`, entrypoint `app/Home.py`, and Python 3.12. The account owner must connect the repository in Streamlit Community Cloud. A reviewed merge to `main` will trigger its normal source update; post-merge Actions checks report failures but cannot hold back a deployment that has already started. Remote hosting is not verified until the live app and commit are observed.
