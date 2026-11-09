# FD001 loader contract

`fleetpulse.data.loader` reads the original, whitespace-separated files described in [the provenance record](fd001_provenance.md). It does not download files, alter them, train models, or load data when imported.

```python
from fleetpulse import PROJECT_ROOT
from fleetpulse.data.loader import load_engine_history

records = load_engine_history(PROJECT_ROOT / "data" / "raw" / "train_FD001.txt")
```

`load_engine_history(path)` returns a list of dictionaries in file order. Each dictionary contains `unit_id` and `cycle` as integers, followed by `setting_1` through `setting_3` and `sensor_1` through `sensor_21` as floats. This is the normalized schema used by `validate_engine_history` and `summarize_engine_history`. The loader rejects a nonempty history line with a different field count or invalid number, reporting its line number. It leaves semantic integrity checks to the quality module. Train and test histories must be kept as separate collections: the same engine number can occur in both.

`load_rul_values(path)` is a separate, explicit reader for a one-column RUL answer file; it returns integer values in file order and never joins them to history records. The history reader does not access this file. The official test answers are not a tuning pool; the automated loader tests use invented answer values only.

The local FD001 histories were checked on 9 November 2026: the training file produced 20,631 rows for 100 distinct engine IDs and the test-history file produced 13,096 rows for 100 distinct engine IDs. Both passed the current quality module with zero errors and zero warnings. These are observed counts, not model scores. The P02-S2 summary did not parse or use real test-answer values. During a later archive-inspection command, output may have exposed the answer file's first lines; see [the summary disclosure](fd001_summary.md). No answer values were used for training, tuning, or reported metrics. The files remain ignored by Git; each checkout needs its own local files.

The later P02-A3 task covers more complete unreadable-file/error handling and train/test/label-length checks. UI integration is tracked separately under P02-T1.
