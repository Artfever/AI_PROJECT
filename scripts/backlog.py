"""Build and validate FleetPulse's source-faithful issue manifest.

The three personal guides and master plan are local inputs, intentionally ignored
by Git. The generated manifest is committed so issue synchronization is repeatable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "FleetPulse_Phase_Implementation_Plan.md"
MANIFEST = ROOT / "planning" / "backlog.json"
PEOPLE = {
    "Abdullah": ("A", "Abdullah-SE-bit"),
    "Shaheer": ("S", "Artfever"),
    "Taha": ("T", "TahaSohail-Goat"),
}
PHASE_RE = re.compile(r"^### (P\d{2})\s+\S+\s+(.+)$", re.MULTILINE)
OWNER_RE = re.compile(r"^\*\*(Abdullah|Shaheer|Taha)\s+\S+\s+([AST]):\s+(.+?)\*\*$", re.MULTILINE)
TASK_RE = re.compile(r"^([123])\.\s+(.+)$", re.MULTILINE)
PHASE_TABLE_RE = re.compile(r"^\| (P\d{2}) \| (.+?) \| (.+?) \|$", re.MULTILINE)

# Explicit producer-to-consumer handoffs in the phase order paragraphs. These
# are technical outputs, not assumptions about which teammate is free first.
CROSS_TASK_DEPS = {
    "P01-S1": ["P01-A2"],
    "P02-S3": ["P02-A2"], "P02-T3": ["P02-A2"],
    "P03-T3": ["P03-A2"],
    "P04-S3": ["P04-A3"], "P04-T3": ["P04-A3"],
    "P05-S1": ["P05-A1"], "P05-T3": ["P05-S3"],
    "P06-S3": ["P06-A3"], "P06-T3": ["P06-A3"],
    "P07-S3": ["P07-A3"], "P07-T3": ["P07-A3"],
    "P08-S3": ["P08-A3"], "P08-T3": ["P08-A3"],
    "P09-A3": ["P09-T3"], "P09-S3": ["P09-T3"],
    "P10-A3": ["P10-S3"], "P10-T3": ["P10-S3"],
    "P11-T3": ["P11-A3", "P11-S3"],
    "P12-T3": ["P12-A3", "P12-S3"],
    "P13-T3": ["P13-S3"],
    "P14-T3": ["P14-A3"],
    "P15-T3": ["P15-A3"],
    "P16-T3": ["P16-A3"],
    "P17-T3": ["P17-S3"],
    "P19-A3": ["P19-S3"],
    "P20-T3": ["P20-A3"],
    "P23-A3": ["P23-T3"], "P23-S3": ["P23-T3"],
    "P26-T3": ["P26-A3", "P26-S3"],
}
EXISTING_EVIDENCE = {
    "P01-A1": ["PR #1 created package/app/test/docs folders; planned data/artifact folders still need inspection."],
    "P01-A2": ["PR #1 added pyproject.toml, README setup, repository-relative PROJECT_ROOT, and ignore rules."],
    "P01-A3": ["PR #1 added a bootstrap configuration/path test and documented setup commands."],
    "P01-S1": ["Local editable install and pytest were run, but a fresh virtual environment was not verified."],
    "P01-S3": ["PR #1 CI passed; closed verification PR #3 showed a failing test blocks ci-gate."],
    "P01-T1": ["PR #1 added app/Home.py; the five planned pages are not present."],
    "P01-T2": ["Home has an explicit missing-data/model state; shared navigation and other pages are not present."],
}


def local_source(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"Missing source: {path}")
    return path.read_text(encoding="utf-8")


def explanation_map(person: str) -> dict[str, str]:
    source = local_source(ROOT / f"{person}.md")
    matches = re.findall(
        r"\*\*Task [123]\s+\S+\s+(P\d{2}-[AST][123])\*\*[\s\S]*?In simple words:\s*(.+)",
        source,
    )
    result = dict(matches)
    if len(result) != 78:
        raise SystemExit(f"{person} guide has {len(result)} task explanations, expected 78")
    return result


def human_checks(person: str) -> dict[str, str]:
    source = local_source(ROOT / f"{person}.md")
    result: dict[str, str] = {}
    for phase in range(1, 27):
        phase_id = f"P{phase:02d}"
        match = re.search(
            rf"FleetPulse AI \| Member: {person} \| Phase: {phase_id} \|[\s\S]*?"
            r"Human responsibility for this packet:\s*(.+)",
            source,
        )
        if not match:
            raise SystemExit(f"Missing human check for {person} {phase_id}")
        result[phase_id] = match.group(1).strip()
    return result


def topological_order(nodes: set[str], edges: dict[str, list[str]]) -> list[str]:
    pending = {node: set(edges.get(node, [])) for node in nodes}
    for node, deps in pending.items():
        unknown = deps - nodes
        if unknown:
            raise SystemExit(f"Unknown dependency for {node}: {sorted(unknown)}")
        if node in deps:
            raise SystemExit(f"Self-dependency: {node}")
    ordered: list[str] = []
    while pending:
        ready = sorted(node for node, deps in pending.items() if not deps)
        if not ready:
            raise SystemExit(f"Dependency cycle: {sorted(pending)}")
        for node in ready:
            ordered.append(node)
            del pending[node]
            for deps in pending.values():
                deps.discard(node)
    return ordered


def evidence_for(requirement: str, task_id: str) -> tuple[str, str]:
    if task_id == "P01-A1":
        return (
            "Inspect the actual repository tree and record which required package, app, test, docs, data, and artifact directories exist; run a clean install check.",
            "Confirm the repository owner, teammate access, agreed Python version, and missing directories with the team.",
        )
    text = requirement.lower()
    if any(word in text for word in ("train", "model", "predict", "scaler", "bundle")):
        return (
            "Run the relevant training/inference or reload check and record actual config, seed, artifact version, and numeric output; never invent a score.",
            "Inspect the saved output and explain model behavior and limitations to a teammate.",
        )
    if any(word in text for word in ("split", "leak", "feature", "rul", "metric", "validation")):
        return (
            "Use a focused synthetic or real-data check for engine identity, past-only inputs, and expected numeric results as applicable; record command and output.",
            "Inspect a small example independently and explain its units and data provenance.",
        )
    if any(word in text for word in ("schedule", "edd", "ga", "tard", "job", "horizon")):
        return (
            "Check a tiny hand-calculated scenario plus schedule feasibility and repeatability where applicable; record actual score and assumptions.",
            "Review synthetic durations, weights, buffers, and capacity assumptions with the team.",
        )
    if any(word in text for word in ("page", "app", "upload", "display", "view", "screen", "chart")):
        return (
            "Run focused service/AppTest or browser checks for the changed UI path and missing/error states; record actual behavior.",
            "Open the affected screen and check that its displayed values match service output.",
        )
    if any(word in text for word in ("report", "slides", "diagram", "audit", "claims")):
        return (
            "Trace every reported claim or figure to a real source artifact and version; record a reviewable audit note.",
            "Human reviewer checks scientific wording, references, and exported layout.",
        )
    return (
        "Run the relevant command or inspection for this exact deliverable and save the observed result and changed paths.",
        "A teammate checks the output against the original requirement.",
    )


def build_manifest() -> dict:
    source = local_source(PLAN)
    section = source.split("## 6. Detailed phases", 1)[1].split("## 7. Shared technical contracts", 1)[0]
    phase_map = source.split("## 4. Phase map and checkpoints", 1)[1].split("## 5. Dependency graphs", 1)[0]
    table = {
        phase: {"increment": outcome, "prerequisites": re.findall(r"P\d{2}", deps)}
        for phase, outcome, deps in PHASE_TABLE_RE.findall(phase_map)
    }
    phase_matches = list(PHASE_RE.finditer(section))
    if len(phase_matches) != 26 or len(table) != 26:
        raise SystemExit(f"Expected 26 phase sections and rows, got {len(phase_matches)}, {len(table)}")
    guides = {person: explanation_map(person) for person in PEOPLE}
    manual = {person: human_checks(person) for person in PEOPLE}
    existing = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    existing_phases = {p["id"]: p for p in existing.get("phases", [])}
    existing_tasks = {t["id"]: t for t in existing.get("tasks", [])}
    phases = []
    tasks = []
    for i, match in enumerate(phase_matches):
        phase_id, title = match.groups()
        block = section[match.end():phase_matches[i + 1].start() if i + 1 < len(phase_matches) else len(section)]
        outcome = re.search(r"\*\*Outcome:\*\*\s*(.+?)\s*\*\*Prerequisites:", block)
        order = re.search(r"^\*\*Order/parallel:\*\*\s*(.+)$", block, re.MULTILINE)
        gate = re.search(r"^\*\*Gate(?: [A-F])?:\*\*\s*(.+)$", block, re.MULTILINE)
        if not (outcome and order and gate):
            raise SystemExit(f"Missing phase outcome/order/gate: {phase_id}")
        owners = list(OWNER_RE.finditer(block))
        if len(owners) != 3:
            raise SystemExit(f"Expected three owners in {phase_id}")
        phase_tasks = []
        for j, owner_match in enumerate(owners):
            person, letter, packet = owner_match.groups()
            if PEOPLE[person][0] != letter:
                raise SystemExit(f"Owner mismatch in {phase_id}")
            owner_block = block[owner_match.end():owners[j + 1].start() if j + 1 < len(owners) else len(block)]
            found = TASK_RE.findall(owner_block)
            if len(found) != 3 or [int(n) for n, _ in found] != [1, 2, 3]:
                raise SystemExit(f"Expected three numbered tasks for {phase_id}-{letter}")
            for number, requirement in found:
                task_id = f"{phase_id}-{letter}{number}"
                previous = f"{phase_id}-{letter}{int(number) - 1}" if number != "1" else None
                deps = ([previous] if previous else []) + CROSS_TASK_DEPS.get(task_id, [])
                automated, human = evidence_for(requirement, task_id)
                old = existing_tasks.get(task_id, {})
                task = {
                    "id": task_id, "phase": phase_id, "owner": person,
                    "assignee": PEOPLE[person][1], "packet": packet,
                    "title": guides[person][task_id].rstrip("."),
                    "explanation": guides[person][task_id],
                    "source_document": PLAN.name,
                    "source_section": f"6 > {phase_id} > {person} {packet}",
                    "original_requirement": requirement.strip(),
                    "phase_prerequisites": table[phase_id]["prerequisites"],
                    "task_dependencies": list(dict.fromkeys(deps)),
                    "phase_order": order.group(1).strip(),
                    "phase_gate": gate.group(1).strip(),
                    "inputs": [table[p]["increment"] for p in table[phase_id]["prerequisites"]],
                    "expected_output": requirement.strip(),
                    "automated_evidence": automated, "manual_evidence": human,
                    "human_responsibility": manual[person][phase_id],
                    "status": old.get("status", "not_verified"),
                    "evidence": old.get("evidence") or EXISTING_EVIDENCE.get(task_id, []),
                    "issue": old.get("issue"),
                }
                tasks.append(task)
                phase_tasks.append(task_id)
        old_phase = existing_phases.get(phase_id, {})
        phases.append({
            "id": phase_id, "title": title.strip(), "increment": table[phase_id]["increment"],
            "outcome": outcome.group(1).strip(),
            "prerequisites": table[phase_id]["prerequisites"],
            "order_parallel": order.group(1).strip(), "gate": gate.group(1).strip(),
            "tasks": phase_tasks, "issue": old_phase.get("issue"),
        })
    task_ids = [task["id"] for task in tasks]
    if len(tasks) != 234 or len(set(task_ids)) != 234:
        raise SystemExit(f"Expected 234 unique tasks, got {len(tasks)}")
    owner_counts = Counter(task["owner"] for task in tasks)
    if set(owner_counts.values()) != {78}:
        raise SystemExit(f"Owner counts not 78 each: {owner_counts}")
    phase_edges = {phase["id"]: phase["prerequisites"] for phase in phases}
    task_edges = {task["id"]: task["task_dependencies"] for task in tasks}
    phase_order = topological_order(set(phase_edges), phase_edges)
    task_order = topological_order(set(task_edges), task_edges)
    return {
        "schema_version": 1,
        "source_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
        "source_document": PLAN.name,
        "guide_sha256": {p: hashlib.sha256((ROOT / f"{p}.md").read_bytes()).hexdigest() for p in PEOPLE},
        "repository": "Artfever/AI_PROJECT",
        "review_rule": "one approving review from another named teammate",
        "native_dependencies": existing.get("native_dependencies", {}),
        "native_subissues": existing.get("native_subissues", {}),
        "phase_order": phase_order, "task_order": task_order,
        "phases": phases, "tasks": tasks,
    }


def save_manifest(manifest: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    temporary = MANIFEST.with_suffix(".tmp")
    temporary.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(MANIFEST)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["build", "validate"])
    args = parser.parse_args()
    manifest = build_manifest()
    if args.command == "build":
        save_manifest(manifest)
    print(f"{len(manifest['phases'])} phases, {len(manifest['tasks'])} tasks, "
          f"owner counts {dict(Counter(t['owner'] for t in manifest['tasks']))}; DAG valid")
