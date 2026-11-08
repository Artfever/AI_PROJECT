---
name: FleetPulse numbered task
about: Use for an agreed numbered task from the current phase plan
title: '[P__-__] '
labels: 'type:task'
assignees: ''
---

<!-- fleetpulse-task-id: P__-__ -->

## Owner, source, and parent phase

## Original requirement and plain-English purpose

## Inputs and blocking issue links

## In scope, out of scope, and implementation steps

## Expected files, functions, or artifacts

## Automated evidence and manual human checks

## Acceptance checklist

- [ ] Original behavior is demonstrated with actual output.
- [ ] Relevant checks and versions are recorded.
- [ ] The owner's handoff file records commits, PR, blockers, and next consumer.

## Parallel work and next consumer

## PR route and review

Branch from current `main` using `feat/<task-id>-<description>` (or `fix/` or `chore/`); PR targets `main`. One other named teammate approves the current revision. Link the issue and use `Closes #N` only when fully complete.

## Scientific/course constraints and completion rule

Close only when the task's own evidence is reviewed. The phase parent remains open until its shared gate passes.
