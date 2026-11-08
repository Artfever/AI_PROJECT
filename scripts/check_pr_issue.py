"""Read-only PR dependency gate for numbered FleetPulse task branches."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = "Artfever/AI_PROJECT"
API = f"repos/{REPO}"
MAP = Path(__file__).resolve().parents[1] / "planning" / "issue-map.json"


def gh(endpoint: str) -> object:
    result = subprocess.run(
        ["gh", "api", endpoint, "-H", "Accept: application/vnd.github+json"],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if result.returncode:
        raise RuntimeError(f"Cannot inspect GitHub dependency state at {endpoint}: {result.stderr.strip()}")
    return json.loads(result.stdout)


def main() -> int:
    head = os.environ["PR_HEAD"]
    if head == "chore/shaheer/issue-backlog":
        print("Issue backlog governance PR: task dependency gate does not apply.")
        return 0
    match = re.fullmatch(r"(?:feat|fix|chore)/(P\d{2}-[AST][123])-[a-z0-9-]+", head)
    if not match:
        print("Branch has no valid numbered task ID.")
        return 1
    task_id = match.group(1)
    mapping = json.loads(MAP.read_text(encoding="utf-8"))
    issue_number = mapping["tasks"][task_id]["number"]
    phase_id = task_id[:3]
    parent_number = mapping["phases"][phase_id]["number"]
    body = os.environ.get("PR_BODY", "")
    issue_reference = rf"(?:#{issue_number}(?!\d)|/issues/{issue_number}(?!\d))"
    if not re.search(issue_reference, body):
        print(f"PR must link {task_id}: https://github.com/{REPO}/issues/{issue_number}")
        return 1
    task = gh(f"{API}/issues/{issue_number}")
    parent = gh(f"{API}/issues/{parent_number}")
    if f"<!-- fleetpulse-task-id: {task_id} -->" not in (task.get("body") or ""):
        print(f"Mapping for {task_id} does not match remote issue #{issue_number}.")
        return 1
    if f"<!-- fleetpulse-phase-id: {phase_id} -->" not in (parent.get("body") or ""):
        print(f"Mapping for {phase_id} does not match remote issue #{parent_number}.")
        return 1
    blockers = gh(f"{API}/issues/{issue_number}/dependencies/blocked_by?per_page=100")
    phase_blockers = gh(f"{API}/issues/{parent_number}/dependencies/blocked_by?per_page=100")
    open_blockers = [item for item in blockers + phase_blockers if item["state"] != "closed"]
    if open_blockers:
        print(f"{task_id} has open hard blockers:")
        for item in open_blockers:
            print(f"- {item['html_url']} ({item['title']})")
        return 1
    print(f"{task_id}: linked issue #{issue_number}; no open native task or phase blockers.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyError, RuntimeError, ValueError) as error:
        print(f"Dependency policy could not be verified: {error}", file=sys.stderr)
        sys.exit(1)
