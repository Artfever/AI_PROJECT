# Abdullah handoff

Updated 9 November 2026. Owner: Abdullah (`Abdullah-SE-bit`).

## P02-A1 work performed by Taha ? 9 November 2026

- At Taha's explicit request because Abdullah was unavailable, Taha is preparing [#34](https://github.com/Artfever/FleetpulseAI/issues/34). The GitHub issue remains assigned to Abdullah; this is not a claim of Abdullah's work, review, or agreement. P01 #6 is closed following Taha's confirmation; this task has no open native phase blocker.
- Downloaded the archive linked by NASA's PCoE repository. Its nested `CMAPSSData.zip` supplied the original `train_FD001.txt`, `test_FD001.txt`, and `RUL_FD001.txt`, extracted without overwriting existing files into this clone's ignored `data/raw/`. No test-answer values were inspected. [Provenance and SHA-256 hashes](docs/fd001_provenance.md) record source, retrieval date, sizes, archive hashes, and raw-file hashes. No raw file is tracked or included in this PR.
- Verification on Python 3.12.16: PowerShell `Get-FileHash` matched all three recorded hashes; `git check-ignore -v` confirmed all three raw files remain ignored; `.venv/Scripts/python.exe -m ruff check .` passed; `.venv/Scripts/python.exe -m pytest -q` passed 12 tests. Model-training and inference checks are NOT APPLICABLE to provenance collection. App launch was NOT RUN because no app code changed.
- Work commit: `f123ee5`. PR [#283](https://github.com/Artfever/FleetpulseAI/pull/283) uses `Closes #34` for the completed provenance work, subject to review and CI. One actual review from another teammate, required CI, and resolved conversations are necessary. Since Taha is the PR author, Shaheer is an eligible reviewer; no approval or dataset-location agreement is claimed. After reviewed merge and #34 closure, P02-A2 #110 can implement the loader; P02-T1 #36 still needs that loader, a reviewed return schema, and real-data checks. Teammates must obtain their own ignored raw files.

## Earlier task and inspected state

P01-A3 [#185](https://github.com/Artfever/FleetpulseAI/issues/185): small configuration test and documented setup commands. Technical work is ready for review on `chore/P01-A3-setup-check`, based on current main `ae48e53`. Working tree was clean at session start. Safely switched to main and ran `git pull --ff-only origin main` before branching. Only root AGENTS applies.

Read AGENTS, Abdullah handoff, README, docs/SETUP, bootstrap tests and pyproject, P01 backlog/dependency ordering, live #185 and its native blockers, manifest P01-A3 record, and the supplied local Abdullah/master-plan P01 guidance. Guides remain ignored. Reviewed teammate handoffs; some historical open-task statements are stale, so live state and actual output take precedence.

GitHub now reports the repository as `Artfever/FleetpulseAI`. The existing origin `https://github.com/Artfever/AI_PROJECT.git` redirects to it. This rename was observed remotely, not performed by this session. Use the canonical repository for current PRs/issues. No repository settings, origin URL, or mass historical-link changes were made.

## Accepted prerequisites

- P01-A1 #32 CLOSED; PR #268 approved by Shaheer (`Artfever`) on head `c165a4e`, merged as `64fb041`. Required PR and post-merge CI passed. A1 supplied the tracked package/app/data/artifact scaffold and team-confirmed Python 3.12/folder/access agreement.
- P01-A2 #108 CLOSED; [PR #269](https://github.com/Artfever/FleetpulseAI/pull/269) approved by Shaheer on final head `01d8f67`, merged as `4e6aa77`. A2 commits `25713ee` and `01d8f67` documented and verified the existing editable-install/path contract. Final PR CI run 42516301468 passed five jobs. Current main also contains Shaheer's handoff merge at `ae48e53`.
- Native blocked-by API for #185 returned only CLOSED #108. P01 has no predecessor phase. Actual merged A2 docs, package configuration, and tests were inspected before editing.
- Existing setup evidence: A2 clean Python 3.12.16 install in relocated checkout with spaces, no PYTHONPATH; outside-CWD import and repository paths passed; fresh pytest 2 passed; pip check passed. No runtime/package/ignore configuration needed recreation.

## Changed files and output

- `tests/test_bootstrap.py`: retains original root/entrypoint and Home-empty-state tests. Adds `test_installed_package_paths_from_another_directory(tmp_path)`, which removes PYTHONPATH, starts a new process with the running Python interpreter from a temporary directory, imports installed fleetpulse, and checks its root and real metadata/entrypoint files. A failed import fails via subprocess check=True. This guards the documented editable-install/CWD contract; no artificial dataset or trivial numeric test.
- `docs/SETUP.md`: focused configuration-check command, what it proves, and how to resolve an uninstalled-package error, with Windows/Linux interpreter distinction. Existing actual installation/full-suite/app commands remain unchanged.
- This handoff records reviewed A2 completion, A3 checks and remaining dependencies. No app behavior, data, model, metrics, or later-phase functionality changed.

## Exact checks and results

All local Python commands use the existing CPython 3.12.16 `.venv` (fleetpulse-ai 0.1.0, pytest 8.4.2, Ruff 0.17.4, Streamlit 1.67.0). Prepend `.venv/Scripts` to this shell PATH for plain commands.

- `python -m pytest -q tests/test_bootstrap.py -k 'project_paths or installed_package_paths'`: PASS, **2 passed, 1 deselected in 0.37s**.
- `python -m pytest -q`: initial PASS, **3 passed in 1.08s**; after import-order correction PASS, **3 passed in 0.91s**. JUnit output is ignored in reports/junit.xml.
- `ruff check .`: initial FAIL, one I001 import-order finding in new test. Corrected import order; rerun PASS, `All checks passed!`.
- `git diff --check`: PASS before commit; cached whitespace check must pass as well.
- Local `streamlit run app/Home.py`: NOT RUN; no app behavior changed. Existing Home AppTest passed, and required PR Streamlit smoke CI remains separate.
- Fresh install NOT REPEATED for this test/docs-only change; A2 already verified unchanged package metadata/runtime from a clean relocated environment. Linux/macOS commands NOT RUN locally on this Windows host.

## Commit, PR and human checks

Work commit `b8e1f6f` pushed. [PR #271](https://github.com/Artfever/FleetpulseAI/pull/271) is OPEN against protected main as Abdullah-SE-bit with `Closes #185`, supplying the setup-test/documentation requirement; issue closure still depends on accepted review and merge. This update records the PR before the handoff commit. Monitor latest-head branch-policy, quality, unit-and-contract-tests, streamlit-smoke, and ci-gate; no CI success or human approval is claimed yet. Record this handoff commit's hash in the next substantive update, avoiding hash-only commits.

Publish via local gh authenticated as Abdullah-SE-bit. Do not send teammate messages or explicit review requests. GitHub may automatically request CODEOWNERS reviewers. One actual approval from Shaheer (`Artfever`) OR Taha (`TahaSohail-Goat`), required CI on latest head, and resolved conversations are required. Abdullah should inspect this diff and the actual output; the peer must check it against #185. No new team decision is needed.

## Next task and precise blockers

- P01-A3 is the last Abdullah P01 task. After its reviewed merge, update from main and verify issue closure; do not close shared P01 from Abdullah's tests alone.
- P02-A1 [#34](https://github.com/Artfever/FleetpulseAI/issues/34) is blocked by OPEN P01 gate [#6](https://github.com/Artfever/FleetpulseAI/issues/6). No dataset download or P02 implementation started.
- Shaheer's P01-S1 [#186](https://github.com/Artfever/FleetpulseAI/issues/186) now has only CLOSED #108 as its native blocker; Taha's P01-T1 [#33](https://github.com/Artfever/FleetpulseAI/issues/33) has no blockers. They are open and belong to their named owners. S2/S3 and T2/T3 follow their own predecessors. All members' real test/app evidence and all nine task outputs are required for the shared P01 gate. Do not silently take over teammate tasks.
