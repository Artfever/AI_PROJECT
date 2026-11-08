"""Render human issue indexes and the stable ID -> GitHub issue mapping."""

from __future__ import annotations

import json
from collections import Counter

from backlog import MANIFEST, ROOT


def link(item: dict) -> str:
    issue = item.get("issue")
    return f"[#{issue['number']}]({issue['url']})" if issue else "not created"


def graph(phases: dict[str, dict], ids: list[str]) -> str:
    lines = ["```mermaid", "flowchart LR"]
    for phase_id in ids:
        phase = phases[phase_id]
        lines.append(f'  {phase_id}["{phase_id} {phase["title"]}"]')
    for phase_id in ids:
        for previous in phases[phase_id]["prerequisites"]:
            lines.append(f"  {previous} --> {phase_id}")
    lines.append("```")
    return "\n".join(lines)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    phases = {phase["id"]: phase for phase in manifest["phases"]}
    tasks = {task["id"]: task for task in manifest["tasks"]}
    mapping = {
        "repository": manifest["repository"],
        "source_sha256": manifest["source_sha256"],
        "phases": {key: value["issue"] for key, value in sorted(phases.items())},
        "tasks": {key: value["issue"] for key, value in sorted(tasks.items())},
    }
    (ROOT / "planning" / "issue-map.json").write_text(
        json.dumps(mapping, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    counts = Counter(task["owner"] for task in tasks.values())
    lines = [
        "# FleetPulse issue backlog", "",
        "The master plan supplies 26 phase gates and 234 numbered tasks: 78 each for Abdullah, Shaheer, and Taha. Issue links below are actual GitHub records. Issues track work; they do not mark it implemented. See `planning/backlog.json` for exact source requirements and `planning/issue-map.json` for stable IDs.",
        "", "## Phase index", "", "| Phase | Parent | Prerequisite gates | Shared outcome |", "| --- | --- | --- | --- |",
    ]
    for phase_id, phase in sorted(phases.items()):
        prior = ", ".join(f"{key} {link(phases[key])}" for key in phase["prerequisites"]) or "none"
        lines.append(f"| {phase_id} | {link(phase)} | {prior} | {phase['increment']} |")
    lines += ["", "## Phase tasks", ""]
    for phase_id, phase in sorted(phases.items()):
        lines += [f"### {phase_id}: {phase['title']} — {link(phase)}", "", f"Gate: {phase['gate']}", ""]
        for person in ("Abdullah", "Shaheer", "Taha"):
            selected = [tasks[task_id] for task_id in phase["tasks"] if tasks[task_id]["owner"] == person]
            lines.append(f"- **{person}:** " + "; ".join(f"{t['id']} {link(t)} — {t['title']}" for t in selected))
        lines.append("")
    lines += ["## Per-person index", ""]
    for person in ("Abdullah", "Shaheer", "Taha"):
        lines += [f"### {person} ({counts[person]} tasks)", "", "| Phase | Three assigned tasks |", "| --- | --- |"]
        for phase_id in sorted(phases):
            selected = [t for t in tasks.values() if t["phase"] == phase_id and t["owner"] == person]
            lines.append(f"| {phase_id} | " + ", ".join(f"{t['id']} {link(t)}" for t in selected) + " |")
        lines.append("")
    lines += [
        "## Initial readiness from open hard blockers", "",
        f"- Abdullah: P01-A1 {link(tasks['P01-A1'])} has no issue blocker. Repository evidence is partial; check its acceptance items before closing. P01-A2 and A3 wait for the preceding Abdullah task.",
        f"- Taha: P01-T1 {link(tasks['P01-T1'])} has no issue blocker. The Home shell exists, but the five pages remain unverified. P01-T2 and T3 wait for their preceding Taha task.",
        f"- Shaheer: no P01 task is free of a hard blocker yet. P01-S1 {link(tasks['P01-S1'])} waits for P01-A2 {link(tasks['P01-A2'])}; S2 waits for S1, and S3 waits for S2. Existing CI and install evidence is partial, not task closure.",
        "", "All P02 and later phase gates wait for their listed predecessor gates. Parallel model packets P08/P09/P10 become technically available only after P07; owner availability is a separate constraint. Readiness changes as reviewed outputs and gates close.", "",
    ]
    (ROOT / "docs" / "ISSUE_BACKLOG.md").write_text("\n".join(lines), encoding="utf-8")
    dependency_lines = [
        "# Dependencies and merge order", "",
        "The source phase graph is acyclic. Native GitHub blocked-by links represent 37 phase edges and 189 numbered task edges after synchronization; each child is a native sub-issue of its phase parent. A task does not depend on its own parent. Predecessor phase gates are linked in task bodies and on parent issues.",
        "", "The master plan's 75 focused-hour figure is an optimistic dependency-only lower bound, not total effort or a date promise. P01-P07 are the foundation. P08/P09/P10 are parallel candidate-model branches after P07. P17 and P20 are provisional critical joins; limited three-person availability may change the actual path.",
        "", "## Foundation and candidate models", "", graph(phases, [f"P{i:02d}" for i in range(1, 14)]),
        "", "## Product and planning", "", graph(phases, ["P07", "P12", "P14", "P15", "P16", "P17", "P18", "P19", "P20", "P21"]),
        "", "## Release joins", "", graph(phases, ["P13", "P17", "P20", "P21", "P22", "P23", "P24", "P25", "P26"]),
        "", "## Actual phase issue references", "", "| Phase | Issue | Hard predecessor phases |", "| --- | --- | --- |",
    ]
    for phase_id, phase in sorted(phases.items()):
        prior = ", ".join(f"{p} {link(phases[p])}" for p in phase["prerequisites"]) or "none"
        dependency_lines.append(f"| {phase_id} | {link(phase)} | {prior} |")
    dependency_lines += [
        "", "## Issue to PR route", "",
        "1. Select one assigned task whose hard predecessor outputs and phase gate are verified. One active implementation task per person is the default.",
        "2. Branch from current `main` as `feat/<task-id>-<description>` (or `fix/` / `chore/`). Do not stack normal implementation PRs on unmerged branches.",
        "3. Implement only the task or a small, clear same-owner packet; run relevant tests and update the owner's handoff file.",
        "4. Open a PR to `main`, link each task issue it truly completes, and record actual evidence. `Closes #N` is for full completion; `Refs #N` is for partial work.",
        "5. One other named teammate approves the latest reviewable revision; required CI and resolved conversations must pass. Native issue dependencies are planning relationships and do not themselves enforce a PR merge gate.",
        "6. After merge, verify issue closure and the phase checklist. A consumer updates from `main` and validates the producer's real interface before relying on it. Close the parent only after all nine tasks and its shared gate have evidence.",
        "", "Independent ready tasks may merge in either order; shared schema/model/scheduler contracts need coordination and revalidation. A person being busy is not a technical dependency. A downstream draft may use labeled temporary fixtures but must revalidate against merged upstream code before merge.", "",
    ]
    (ROOT / "docs" / "DEPENDENCIES_AND_MERGE_ORDER.md").write_text("\n".join(dependency_lines), encoding="utf-8")
    print(f"Rendered issue map and indexes: {len(phases)} phases, {len(tasks)} tasks")


if __name__ == "__main__":
    main()
