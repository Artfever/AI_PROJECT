# FD001 dataset notes

## Scope and sources

This note describes the NASA C-MAPSS FD001 simulated turbofan histories used by
FleetPulse. The retrieval details and SHA-256 source hashes are in
[FD001 provenance](fd001_provenance.md). Local train and test history files
remain untracked; regenerate the tracked quality evidence with:

```powershell
python scripts/generate_fd001_quality_report.py
```

The generator reads only `data/raw/train_FD001.txt` and
`data/raw/test_FD001.txt`. It does not open `RUL_FD001.txt`.

## Observed counts

| Split | Rows observed | Engines observed | Rows per engine | Observed cycle range | Quality errors | Cycle-gap warnings |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| Train | 20,631 | 100 | 128–362 | 1–362 | 0 | 0 |
| Test history | 13,096 | 100 | 31–303 | 1–303 | 0 | 0 |

These counts and ranges are observations from the files identified by hash in
[`artifacts/data_quality.json`](../artifacts/data_quality.json). They are not
expected benchmark counts or acceptance targets. The JSON records the full
per-engine counts and cycle ranges, sensor population variances, and every
validator finding. No rows or sensor channels were removed.

## Checks represented in the report

The current validator checks the normalized FD001 columns, positive integral
engine identifiers and cycle numbers, numeric finite settings and sensor
readings, duplicate engine-cycle pairs, and cycle order. A missing cycle is a
warning so that its cause can be reviewed; malformed records, duplicates, and
non-increasing cycles are errors. Validation preserves the supplied records.
Sensor variance is population variance (`ddof=0`) within each split. Only
exactly zero variance is called constant; no threshold is used to label a
sensor as “barely changing.”

## Limits and handling note

This descriptive audit does not establish physical causes, predictive
performance, or model readiness. FD001 is simulated data. The test RUL answers
are separate labels and were not read by this report generator. An earlier
archive-inspection command may have emitted answer-file lines to tool output;
that incident and the restriction on use are disclosed in the
[summary note](fd001_summary.md). No answer values are included in this audit.
