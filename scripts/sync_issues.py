"""Idempotently publish planning/backlog.json as GitHub Issues using gh auth.

Run `python scripts/backlog.py build` first, then `python scripts/sync_issues.py sync`.
Every successful create/link is checkpointed in the manifest immediately.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
import time
from pathlib import Path

from backlog import MANIFEST, save_manifest

REPO = "Artfever/AI_PROJECT"
API = f"repos/{REPO}"
MARKER = re.compile(r"<!-- fleetpulse-(phase|task)-id: (P\d{2}(?:-[AST][123])?) -->")
MUTATION_DELAY = 0.35
AREA = {
    **{f"P{x:02d}": "data" for x in range(2, 6)},
    **{f"P{x:02d}": "ml" for x in range(6, 13)},
    "P13": "evaluation", "P14": "streamlit", "P15": "streamlit",
    "P16": "streamlit", "P17": "evaluation", "P18": "optimization",
    "P19": "optimization", "P20": "optimization", "P21": "streamlit",
    "P22": "evaluation", "P23": "deployment", "P24": "evaluation",
    "P25": "documentation", "P26": "documentation",
}


def gh(endpoint: str, *, method: str = "GET", payload: dict | None = None) -> object:
    command = ["gh", "api", endpoint, "-H", "Accept: application/vnd.github+json"]
    request_path = None
    if method != "GET":
        command += ["-X", method]
    if payload is not None:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".json", delete=False) as handle:
            json.dump(payload, handle, ensure_ascii=False)
            request_path = Path(handle.name)
        command += ["--input", str(request_path)]
    try:
        for attempt in range(5):
            completed = subprocess.run(command, check=False, capture_output=True, text=True, encoding="utf-8")
            if completed.returncode == 0:
                if method != "GET":
                    time.sleep(MUTATION_DELAY)
                return json.loads(completed.stdout) if completed.stdout.strip() else None
            error = completed.stderr.strip()
            recoverable_http = any(code in error for code in ("HTTP 403", "HTTP 429", "HTTP 502", "HTTP 503"))
            recoverable_read = method == "GET" and any(
                phrase in error.lower() for phrase in (
                    "tls handshake timeout", "connection was forcibly closed", "connection reset",
                    "i/o timeout", "unexpected eof", "timeout awaiting response headers",
                )
            )
            if recoverable_http or recoverable_read:
                wait = min(10 * (attempt + 1), 40)
                print(f"Transient GitHub error; retrying {endpoint} in {wait}s", flush=True)
                time.sleep(wait)
                continue
            raise RuntimeError(f"gh api {method} {endpoint}: {error}")
        raise RuntimeError(f"gh api {method} {endpoint}: retries exhausted")
    finally:
        if request_path:
            request_path.unlink(missing_ok=True)


def all_issues() -> tuple[dict[str, dict], dict[str, dict]]:
    markers: dict[str, dict] = {}
    titles: dict[str, dict] = {}
    page = 1
    while True:
        batch = gh(f"{API}/issues?state=all&per_page=100&page={page}")
        if not isinstance(batch, list) or not batch:
            break
        for issue in batch:
            if "pull_request" in issue:
                continue
            marker = MARKER.search(issue.get("body") or "")
            if marker:
                issue_id = marker.group(2)
                if issue_id in markers:
                    raise RuntimeError(f"Duplicate issue marker {issue_id}: #{markers[issue_id]['number']} and #{issue['number']}")
                markers[issue_id] = issue
            title = issue.get("title", "")
            title_match = re.match(r"^\[(P\d{2}(?:-[AST][123])?)\]", title)
            if title_match:
                titles[title_match.group(1)] = issue
        page += 1
    return markers, titles


def issue_link(item: dict) -> str:
    issue = item.get("issue")
    return f"[#{issue['number']}]({issue['url']})" if issue else f"`{item['id']}` (not created)"


def phase_body(phase: dict, phases: dict[str, dict], tasks: dict[str, dict]) -> str:
    prior = [f"- {p}: {issue_link(phases[p])} — {phases[p]['increment']}" for p in phase["prerequisites"]]
    grouped = []
    for person in ("Abdullah", "Shaheer", "Taha"):
        grouped.append(f"### {person}")
        for task_id in phase["tasks"]:
            task = tasks[task_id]
            if task["owner"] == person:
                grouped.append(f"- [ ] {task_id}: {issue_link(task)} — {task['title']}")
    return "\n".join([
        f"<!-- fleetpulse-phase-id: {phase['id']} -->",
        f"# {phase['id']}: {phase['title']}",
        "", "## Outcome", phase["outcome"],
        "", "## Hard predecessor phase gates", *(prior or ["None."]),
        "", "## Nine owned tasks", *grouped,
        "", "## Ordering and parallel work", phase["order_parallel"],
        "", "## Shared acceptance gate", phase["gate"],
        "", "## Completion rule",
        "Keep this parent open until all nine task outcomes and the shared gate have real evidence. A merged child PR alone does not close the phase.",
        "", "Source: `FleetPulse_Phase_Implementation_Plan.md`, section 6.", "",
    ])


def task_body(task: dict, phases: dict[str, dict], tasks: dict[str, dict]) -> str:
    prior_phase = [f"- Phase gate {p}: {issue_link(phases[p])} — {phases[p]['increment']}" for p in task["phase_prerequisites"]]
    prior_task = [f"- {p}: {issue_link(tasks[p])} — output: {tasks[p]['expected_output']}" for p in task["task_dependencies"]]
    paths = sorted(set(re.findall(r"`([^`]+)`", task["original_requirement"])))
    path_text = [f"- Proposed: `{path}` (confirm in code before implementation)." for path in paths]
    evidence = [f"- {item}" for item in task["evidence"]]
    owner = task["owner"]
    other_reviewers = {"Abdullah": "Shaheer or Taha", "Shaheer": "Abdullah or Taha", "Taha": "Abdullah or Shaheer"}[owner]
    return "\n".join([
        f"<!-- fleetpulse-task-id: {task['id']} -->",
        f"# {task['id']}: {task['title']}",
        "", "## Identity and source",
        f"- Phase: {task['phase']} — {issue_link(phases[task['phase']])}",
        f"- Responsible human and assignee: {owner} (`@{task['assignee']}`).",
        f"- Source: `{task['source_document']}`, section {task['source_section']}.",
        f"- Plain-English purpose: {task['explanation']} This contributes to the phase outcome: {phases[task['phase']]['outcome']}",
        "", "## Original task requirement", task["original_requirement"],
        "", "## In scope", f"Deliver and verify this specific requirement: {task['original_requirement']}",
        "", "## Out of scope", "Other numbered tasks and the shared phase gate remain separate; do not claim absent data, trained models, metrics, or deployment.",
        "", "## Required inputs and upstream interfaces", *(prior_phase or ["No predecessor phase gate."]),
        *(prior_task or ["No task-level blocker."]),
        "", "## Implementation steps",
        "1. Inspect the actual upstream outputs and agree the input/output contract with the next consumer.",
        f"2. {task['original_requirement']}",
        "3. Run the focused checks below, record actual versions/results, and update the owner's handoff.",
        "", "## Expected files, functions, or artifacts",
        *(path_text or [f"- Deliverable: {task['expected_output']} Record actual paths/interfaces in the PR and handoff."]),
        "", "## Automated checks or evidence", task["automated_evidence"],
        "", "## Manual human checks", task["manual_evidence"], task["human_responsibility"],
        "", "## Acceptance checklist",
        f"- [ ] The original {task['id']} requirement is demonstrated with actual output.",
        f"- [ ] {task['automated_evidence']}",
        f"- [ ] {task['manual_evidence']}",
        "- [ ] Record the observed results, versions, and limitations rather than planned results.",
        f"- [ ] `{f'handoff_{owner}.md'}` records the commit/PR, tests, blockers, and next consumer.",
        "- [ ] One other named teammate approves the current PR revision and required CI passes.",
        "", "## Blocking dependencies", *(prior_phase + prior_task or ["None."]),
        "", "## Work that may proceed in parallel", task["phase_order"],
        "", "## Required handoff and next consumer",
        f"Update `handoff_{owner}.md`; link the next task/phase that consumes this output. The phase parent stays open until its shared gate passes.",
        "", "## PR route and review",
        f"Branch from current `main` using `feat/{task['id']}-short-description` (or `fix/` / `chore/` as appropriate); PR targets `main`. One approving review from {other_reviewers} is required. Link this issue; use `Closes` only when fully complete.",
        "", "## Scientific/course constraints",
        "Software-only Path A; NASA FD001 is simulated; RUL is measured in cycles. Preserve engine separation, past-only inputs, reproducibility, honest model/evaluation provenance, and labeled synthetic scheduling assumptions where applicable. No invented results or safety claims.",
        "", "## Existing evidence and status", f"Status: {task['status']}; evidence is not acceptance or issue closure.",
        *(evidence or ["- No implementation evidence verified for this task."]),
        "", "## When complete",
        "Close only after this task's acceptance evidence is reviewed and recorded. A non-code task may close after its real artifact and human review; do not create an empty PR.", "",
    ])


def labels_for(item: dict, *, phase: bool) -> list[str]:
    phase_id = item["id"] if phase else item["phase"]
    area = AREA.get(phase_id, "documentation")
    labels = ["type:phase" if phase else "type:task", f"phase:{phase_id}", f"area:{area}"]
    if not phase:
        labels.append(f"owner:{item['owner'].lower()}")
    if int(phase_id[1:]) <= 7:
        labels.append("priority:foundation")
    elif phase_id in {"P11", "P12", "P17", "P20", "P21", "P23", "P24", "P25", "P26"}:
        labels.append("priority:critical-estimate")
    else:
        labels.append("priority:parallel")
    return labels


def ensure_labels() -> None:
    existing = {label["name"] for label in gh(f"{API}/labels?per_page=100")}
    definitions = {
        "type:phase": ("7057ff", "Shared phase tracking issue"),
        "type:task": ("1d76db", "Single-owner numbered task"),
        "priority:foundation": ("b60205", "Foundation prerequisite work"),
        "priority:critical-estimate": ("d93f0b", "Estimated critical-path work"),
        "priority:parallel": ("fbca04", "Potential parallel work; verify readiness"),
        **{f"owner:{name.lower()}": ("c5def5", f"Task owned by {name}") for name in ("abdullah", "shaheer", "taha")},
        **{f"area:{name}": ("bfdadc", f"{name} area") for name in ("data", "ml", "evaluation", "streamlit", "optimization", "deployment", "documentation")},
        **{f"phase:P{i:02d}": ("ededed", f"FleetPulse phase P{i:02d}") for i in range(1, 27)},
    }
    for name, (color, description) in definitions.items():
        if name not in existing:
            gh(f"{API}/labels", method="POST", payload={"name": name, "color": color, "description": description})
            print(f"Created label {name}", flush=True)


def record_issue(item: dict, issue: dict, manifest: dict) -> None:
    item["issue"] = {"id": issue["id"], "number": issue["number"], "url": issue["html_url"]}
    save_manifest(manifest)
    print(f"Mapped {item['id']} -> #{issue['number']}", flush=True)


def ensure_issue(item: dict, *, parent: bool, phases: dict[str, dict], tasks: dict[str, dict],
                 markers: dict[str, dict], titles: dict[str, dict], manifest: dict) -> None:
    issue_id = item["id"]
    prior = markers.get(issue_id) or titles.get(issue_id)
    if prior:
        if not item.get("issue") or item["issue"]["id"] != prior["id"]:
            record_issue(item, prior, manifest)
        return
    body = phase_body(item, phases, tasks) if parent else task_body(item, phases, tasks)
    request = {"title": f"[{issue_id}] {item['title']}", "body": body, "labels": labels_for(item, phase=parent)}
    if not parent:
        request["assignees"] = [item["assignee"]]
    try:
        issue = gh(f"{API}/issues", method="POST", payload=request)
    except RuntimeError:
        # A timed-out create may still have succeeded. Re-read markers before retrying.
        new_markers, new_titles = all_issues()
        issue = new_markers.get(issue_id) or new_titles.get(issue_id)
        if not issue:
            raise
    record_issue(item, issue, manifest)
    markers[issue_id] = issue


def sync(manifest: dict, *, max_tasks: int | None = None) -> None:
    ensure_labels()
    markers, titles = all_issues()
    phases = {phase["id"]: phase for phase in manifest["phases"]}
    tasks = {task["id"]: task for task in manifest["tasks"]}
    for phase_id in manifest["phase_order"]:
        ensure_issue(phases[phase_id], parent=True, phases=phases, tasks=tasks,
                     markers=markers, titles=titles, manifest=manifest)
    count = 0
    for task_id in manifest["task_order"]:
        if max_tasks is not None and count >= max_tasks:
            break
        ensure_issue(tasks[task_id], parent=False, phases=phases, tasks=tasks,
                     markers=markers, titles=titles, manifest=manifest)
        count += 1
    if count != len(tasks):
        print(f"Partial task sync: {count}/{len(tasks)}; rerun without --max-tasks", flush=True)
        return
    native_children = manifest.setdefault("native_subissues", {})
    for task in manifest["tasks"]:
        if native_children.get(task["id"]):
            continue
        parent = phases[task["phase"]]
        endpoint = f"{API}/issues/{parent['issue']['number']}/sub_issues"
        try:
            gh(endpoint, method="POST", payload={"sub_issue_id": task["issue"]["id"]})
        except RuntimeError:
            existing = gh(f"{endpoint}?per_page=100")
            if not any(item["id"] == task["issue"]["id"] for item in existing):
                raise
        native_children[task["id"]] = True
        save_manifest(manifest)
        print(f"Parented {task['id']} to {task['phase']}", flush=True)
    # Parents are first created with stable IDs, then patched once with real child links.
    for phase in manifest["phases"]:
        body = phase_body(phase, phases, tasks)
        remote = markers[phase["id"]]
        if remote["body"] != body:
            gh(f"{API}/issues/{phase['issue']['number']}", method="PATCH", payload={"body": body})
            print(f"Indexed {phase['id']} children", flush=True)
    for task in manifest["tasks"]:
        body = task_body(task, phases, tasks)
        remote = markers[task["id"]]
        if remote["body"] != body:
            gh(f"{API}/issues/{task['issue']['number']}", method="PATCH", payload={"body": body})
            print(f"Updated {task['id']} source context", flush=True)
    # Native dependencies: all 37 phase edges and 189 same/cross-owner task edges.
    # A task is never blocked by its own parent; predecessor phase gates are
    # linked on parents and stated in each task body.
    native = manifest.setdefault("native_dependencies", {})
    for phase in manifest["phases"]:
        for predecessor in phase["prerequisites"]:
            add_dependency(phase, phases[predecessor], native, manifest)
    for task in manifest["tasks"]:
        for predecessor in task["task_dependencies"]:
            add_dependency(task, tasks[predecessor], native, manifest)


def add_dependency(blocked: dict, blocker: dict, native: dict, manifest: dict) -> None:
    key = f"{blocked['id']}<-{blocker['id']}"
    if native.get(key):
        return
    endpoint = f"{API}/issues/{blocked['issue']['number']}/dependencies/blocked_by"
    try:
        gh(endpoint, method="POST", payload={"issue_id": blocker["issue"]["id"]})
    except RuntimeError:
        existing = gh(f"{endpoint}?per_page=100")
        if not any(item["id"] == blocker["issue"]["id"] for item in existing):
            raise
    native[key] = True
    save_manifest(manifest)
    print(f"Linked {key}", flush=True)


def audit(manifest: dict) -> None:
    markers, _ = all_issues()
    phases = {phase["id"]: phase for phase in manifest["phases"]}
    tasks = {task["id"]: task for task in manifest["tasks"]}
    if len(markers) != 260:
        raise SystemExit(f"Remote marked issue count {len(markers)}, expected 260")
    for task in tasks.values():
        issue = markers.get(task["id"])
        if not issue:
            raise SystemExit(f"Missing remote task {task['id']}")
        if [person["login"] for person in issue["assignees"]] != [task["assignee"]]:
            raise SystemExit(f"Assignee mismatch {task['id']}")
        if issue["body"] != task_body(task, phases, tasks):
            raise SystemExit(f"Body mismatch {task['id']}")
        if issue["state"] != "open":
            raise SystemExit(f"Unexpected closed task {task['id']}")
        expected_labels = set(labels_for(task, phase=False))
        if not expected_labels.issubset({label["name"] for label in issue["labels"]}):
            raise SystemExit(f"Label mismatch {task['id']}")
    for phase in phases.values():
        issue = markers.get(phase["id"])
        if not issue or issue["assignees"]:
            raise SystemExit(f"Missing/assigned parent {phase['id']}")
        if issue["body"] != phase_body(phase, phases, tasks):
            raise SystemExit(f"Body mismatch {phase['id']}")
        if any(f"#{tasks[task_id]['issue']['number']}" not in issue["body"] for task_id in phase["tasks"]):
            raise SystemExit(f"Missing child index in {phase['id']}")
        if issue["state"] != "open":
            raise SystemExit(f"Unexpected closed phase {phase['id']}")
        expected_labels = set(labels_for(phase, phase=True))
        if not expected_labels.issubset({label["name"] for label in issue["labels"]}):
            raise SystemExit(f"Label mismatch {phase['id']}")
        children = gh(f"{API}/issues/{issue['number']}/sub_issues?per_page=100")
        actual_children = {child["id"] for child in children}
        expected_children = {tasks[task_id]["issue"]["id"] for task_id in phase["tasks"]}
        if actual_children != expected_children:
            raise SystemExit(f"Native sub-issue mismatch {phase['id']}: {len(actual_children)}/9")
    expected_edges = sum(len(p["prerequisites"]) for p in phases.values()) + sum(len(t["task_dependencies"]) for t in tasks.values())
    for item, predecessors, index in (
        *((phase, phase["prerequisites"], phases) for phase in phases.values()),
        *((task, task["task_dependencies"], tasks) for task in tasks.values()),
    ):
        if not predecessors:
            continue
        endpoint = f"{API}/issues/{item['issue']['number']}/dependencies/blocked_by?per_page=100"
        actual = {blocker["id"] for blocker in gh(endpoint)}
        expected = {index[predecessor]["issue"]["id"] for predecessor in predecessors}
        if actual != expected:
            raise SystemExit(f"Native dependency mismatch {item['id']}: {len(actual)}/{len(expected)}")
    if len(manifest.get("native_dependencies", {})) != expected_edges:
        raise SystemExit(f"Only {len(manifest.get('native_dependencies', {}))}/{expected_edges} native links checkpointed")
    print(f"Remote audit: {len(phases)} parents, {len(tasks)} tasks, 78 per owner, 234 native sub-issues, {expected_edges} native dependencies verified")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["sync", "audit"])
    parser.add_argument("--max-tasks", type=int)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if args.command == "sync":
        sync(manifest, max_tasks=args.max_tasks)
    else:
        audit(manifest)
