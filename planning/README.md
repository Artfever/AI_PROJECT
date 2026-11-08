# Backlog data

`backlog.json` is the checked, source-derived record of all 26 phases and 234 numbered tasks. `issue-map.json` maps those stable IDs to the published GitHub issue numbers, database IDs, and URLs. Neither file contains credentials. The original master plan and personal guides stay local and ignored by Git.

From the repository root, `python scripts/backlog.py validate` checks the local source documents and dependency graph. `python scripts/backlog.py build` regenerates the manifest while preserving known issue mappings and native-link checkpoints. `python scripts/sync_issues.py sync` publishes missing records and relationships; reruns use the stable markers. `python scripts/sync_issues.py audit` reads GitHub to verify counts, assignment, labels, parent links, and dependency links. `python scripts/render_backlog.py` regenerates the human indexes after the remote sync.

Use `gh auth status` before remote commands. Do not close issues or mark work verified from this plan alone. The code and reviewed evidence determine completion.
