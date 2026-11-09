# Observed FD001 history summary

This report summarizes the hashed train and test **history** files from NASA C-MAPSS FD001. The source and retrieval record is in [fd001_provenance.md](fd001_provenance.md); loader behavior is described in [fd001_loader.md](fd001_loader.md). Complete per-engine counts/ranges, source hashes, and quality findings are in [fd001_summary.json](fd001_summary.json).

## Observed coverage

| Split | Rows observed | Engines observed | Rows per engine | First cycle range | Last cycle range | Quality errors | Quality warnings |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Train | 20,631 | 100 | 128-362 | 1-1 | 128-362 | 0 | 0 |
| Test | 13,096 | 100 | 31-303 | 1-1 | 31-303 | 0 | 0 |

These are **observed counts**, derived from the files listed in the JSON audit. They are not presented as expected benchmark counts. The full JSON records each engine ID, its row count, and its first/last observed cycle. The quality validator reported no errors or cycle-gap warnings in either history. No rows or sensor channels were dropped.

## Sensor population variance

Variance uses all rows within each split and `ddof=0`. Values are in each sensor's squared units; scales differ across sensors, so variance magnitudes should not be compared as if the sensors shared a unit. Exact zero variance is reported without an arbitrary "barely changes" threshold.

| Sensor | Train variance | Test variance |
| --- | ---: | ---: |
| sensor_1 | 0 | 0 |
| sensor_2 | 0.250041152629 | 0.160708010004 |
| sensor_3 | 37.5891723692 | 25.0308385392 |
| sensor_4 | 81.0069597573 | 44.7300653852 |
| sensor_5 | 0 | 0 |
| sensor_6 | 1.92918557413e-06 | 2.90368311597e-06 |
| sensor_7 | 0.783350333159 | 0.464115320947 |
| sensor_8 | 0.00503869397222 | 0.00329930661413 |
| sensor_9 | 487.629931185 | 130.778067842 |
| sensor_10 | 0 | 0 |
| sensor_11 | 0.0713322208184 | 0.0383806360729 |
| sensor_12 | 0.543958639 | 0.313158189101 |
| sensor_13 | 0.00517207972839 | 0.00324126817218 |
| sensor_14 | 363.882851337 | 103.799744768 |
| sensor_15 | 0.00140655969147 | 0.000841476825247 |
| sensor_16 | 0 | 0 |
| sensor_17 | 2.39855064123 | 1.52159558809 |
| sensor_18 | 0 | 0 |
| sensor_19 | 0 | 0 |
| sensor_20 | 0.0326676876851 | 0.0200719036324 |
| sensor_21 | 0.0117176838906 | 0.00707568119889 |

Exactly constant in both splits: `sensor_1`, `sensor_5`, `sensor_10`, `sensor_16`, `sensor_18`, and `sensor_19`. The summary preserves these channels; no feature-selection or physical-cause conclusion is made here.

## Scope and integrity note

This is a descriptive data-quality report, not model training or evaluation. The summary calculation loads only `train_FD001.txt` and `test_FD001.txt`; it does not parse or use `RUL_FD001.txt`. During this session, an earlier archive-inspection shell command used a PowerShell `-Include` filter that did not narrow the files as intended and may have emitted the answer file's first lines to tool output. No answer values were used in this summary or any model, and they are excluded from the JSON report. This incidental exposure is recorded so later evaluation work can account for it.

Reproduced from the original-format source files whose byte sizes and SHA-256 hashes are recorded in the JSON. The summary code was run from repository commit `d33c790a6ba28b63b5c253f816560cbb5b0245a1` on 2026-11-09.
