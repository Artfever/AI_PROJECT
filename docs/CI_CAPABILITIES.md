# CI capability inventory

| Capability | Current automated check | Status |
| --- | --- | --- |
| Package install and repository paths | editable install, bootstrap test | Active |
| Streamlit empty state | AppTest | Active |
| Streamlit process starts | bounded health smoke | Active |
| PR branch route to main | branch-policy | Active after workflow merge |
| One teammate review | Native protected-branch rule | Configured remotely; live approval test awaits a teammate |
| Data, labels, features, models, evaluation | None; phases P02–P17 | Not implemented |
| Fleet and scheduling | None; phases P15–P20 | Not implemented |
| Full UI and final release evidence | None; phases P21–P26 | Not implemented |

When a capability lands, its tests must become required. Removing an implemented capability or test requires an explicit reviewed scope change. Final academic release readiness also needs frozen artifacts, official evaluation evidence, report, slides, public deployment, and live human checks.
