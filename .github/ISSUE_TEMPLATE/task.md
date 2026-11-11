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

Branch from current `dev` using a descriptive name; task PR targets `dev`. Teammate approval is not required on task PRs; required CI and resolved conversations still apply. Link the issue and use `Refs #N` on the task PR. Close the issue only when its work and evidence are complete and merged to `dev`. After all phase tasks and the shared gate are verified, promote `dev` to protected `main` through a phase PR with one teammate approval.

## Scientific/course constraints and completion rule

Close only when the task's own evidence is reviewed. The phase parent remains open until its shared gate passes.
