# FD001 raw and demo data

## Get the raw files

The app currently reads the original simulated NASA C-MAPSS FD001 training history from `data/raw/train_FD001.txt` in this clone. The raw files are not included in Git. To set up a fresh checkout:

1. Download **Turbofan Engine Degradation Simulation** from the [NASA PCoE dataset repository](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/).
2. Open the downloaded archive, then its nested `CMAPSSData.zip`. Extract the original `train_FD001.txt` into this clone's `data/raw/` directory. Preserve its bytes; do not edit the source file.
3. Compare the file's SHA-256 with [the provenance record](fd001_provenance.md). If an existing file differs, keep it and investigate before replacing it.
4. Start or refresh the app. Home and Engine Explorer will show counts and a preview when the file loads and passes the current quality checks.

The source archive also includes `test_FD001.txt` and `RUL_FD001.txt`. They may be stored alongside the training file for later work, but the current UI does not load them. The RUL file contains official test answers and must not be used for training or tuning. The three raw files and their hashes are documented separately in the provenance record.

If the app reports a missing, unreadable, malformed, or invalid file, check the location, read permissions, file format and hash. A ZIP file or a renamed file is not a substitute for the extracted original. The app does not fabricate counts when loading fails.

## Demo and test data

The explicitly selected `Illustrative synthetic example` on the prediction page reads `data/demo/illustrative_history.txt`. It contains the three artificial rows of the existing project-created fixture `tests/fixtures/synthetic_engine_history.csv`, converted to the existing whitespace format. These invented numbers are not NASA observations, are not a model-training set, and are not representative engine readings. Their purpose is to exercise the interface. A saved trained bundle must still be supplied separately, and predictions on these out-of-distribution values cannot establish model quality or the Phase 7 real-data parity gate. The UI labels this distinction and uses `illustrative/synthetic` as its partition.

The explicitly selected `Packaged FD001/train parity subset` reads `data/demo/fd001_training_prefixes.txt`. It contains only original simulated training readings from engine 4 cycles 1–164, engine 5 cycles 1–58, and engine 12 cycles 1–7 (229 rows total). The owner approved including this small subset for the public deployment demonstration on 13 November 2026. The packaging script checks the original `train_FD001.txt` hash, preserves selected source rows, and rejects missing cycles or any unexpected source. The subset is not a complete dataset, validation split, test partition, or evidence of model quality. It includes no official test histories or RUL answers.

The NASA [PCoE source page](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/) identifies and distributes the dataset but does not state a dataset-specific redistribution license. Owner approval records the project's choice to package this limited demonstration subset; it does not assert a NASA license. The original complete training file and all other data/demo contents remain ignored; only `.gitkeep`, `illustrative_history.txt`, and the explicitly approved parity subset are tracked in `data/demo/`.
