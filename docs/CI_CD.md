# CI and delivery

Development CI runs on PRs to `dev` and `main`, pushes to both, and manual dispatch. The check names are `branch-policy`, `quality`, `unit-and-contract-tests`, `streamlit-smoke`, and `ci-gate`. The separate trusted review workflow publishes the `review-policy` commit status. Required checks should be set only after real runs register them on GitHub.

The test job uploads `reports/junit.xml` even on failure. The gate writes a job summary with each dependency result. The smoke job starts `app/Home.py`, probes `/_stcore/health`, captures the log on failure, and stops the process. PR code runs with read only permissions. The review workflow reads PR metadata without checking out PR code.

Streamlit Community Cloud should be configured for this repository, branch `main`, entrypoint `app/Home.py`, and Python 3.12. The account owner must connect the repository in Streamlit Community Cloud. A reviewed merge to `main` will trigger its normal source update; post merge Actions checks report failures but cannot hold back a deployment that has already started. Remote hosting is not verified until the live app and commit are observed.

## Protection completion after bootstrap review

The owner must invite `TahaSohail-Goat` as a collaborator and wait for acceptance. Once both teammates approve and merge the setup PR into `dev`, confirm the real job names from its Actions run. In repository Settings → Branches, configure **both** `dev` and `main` to require `branch-policy`, `quality`, `unit-and-contract-tests`, `streamlit-smoke`, and `ci-gate`. After the trusted review workflow runs from the protected base, additionally require `review-policy`. Keep strict up-to-date checks, two approving reviews, stale approval dismissal, latest push approval, conversation resolution, administrator enforcement, force-push ban, and deletion ban. Do not require a check before its first successful run or weaken the review count to merge bootstrap work.

Keep `main` as the default branch until the trusted workflow is promoted there, or move the default to `dev` after the setup PR merges so GitHub discovers review events there. In either case, verify review submissions and dismissals change the `review-policy` status on the current head. Inspect the effective protection through `gh api repos/Artfever/AI_PROJECT/branches/main/protection` and the matching `/dev/protection` endpoint. GitHub owner level settings can still be altered by the owner.
