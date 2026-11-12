# FleetPulse AI: initial user journey

FleetPulse is an early Streamlit shell for exploring simulated turbofan engine histories and maintenance planning. When the local FD001 training file is present, Home and Engine Explorer show its actual row and engine counts and a preview. The app does not yet generate predictions, evaluate models, or produce schedules.

## Current experience

Start the app from the repository root with `python -m streamlit run app/Home.py`. Use the sidebar to open:

1. **Home** introduces the project, reports that trained models and evaluation results are unavailable, and shows a training-history summary when the local file is available.
2. **Fleet Overview** identifies the future fleet view and the absence of fleet data and predictions.
3. **Engine Explorer** shows the training-history counts and preview and lets the user select a training engine to see its records sorted by cycle. Sensor views chart original channels against operating cycle. The development feature preview shows a selected training engine?s visible history and its calculated past-only features. A separate training-ground-truth tab displays uncapped known training RUL in cycles for analysis only; it is not a prediction or a model input. It explains why data could not be loaded when the file is missing or malformed.
4. **RUL Prediction** identifies remaining useful life in operating cycles and the absence of a trained model and predictions.
5. **Maintenance Planner** identifies the future simulated scheduling view and the absence of schedules.
6. **Model Laboratory** shows the verified development split manifest, validation cutoffs, prefix lengths and known target range when the matching training file is available. After the documented P06 run, it verifies and compares the constant baseline and bounded Decision Tree on the same held-out development engines, including per-engine predicted-versus-actual RUL. Target and lifetime metadata are for analysis, not model inputs. These are development-validation results, not official-test performance.

The sidebar lets the user move between pages. Missing or malformed local training data produces a message without fabricated counts, with [setup and demo-data guidance](data_policy.md). No data upload, prediction, comparison, or scheduling control is implemented yet.

## Intended future journey

As the relevant phases are implemented and reviewed, a user is intended to select or provide an engine history, inspect its readings, request a remaining-useful-life prediction from a saved model, and explore the prediction and available evaluation evidence. A fleet view is intended to bring engine predictions together; a simulated maintenance planner is intended to compare schedules using clearly identified scenario assumptions. The Model Laboratory is intended to show actual model-development and evaluation results when available.

These are planned steps, not current features. Data, synthetic scenario assumptions, predictions, and measured evaluation results must remain clearly distinguishable. Remaining useful life is measured in operating cycles. The project uses simulated turbofan data and is not a certified aircraft maintenance system.

## Verification and human review

The automated page checks run from the project root with `python -m pytest -q`; they exercise Home, each page, and returning to Home without requiring data or models. Taha confirmed in chat on 9 November 2026 that he tested the pages after the navigation update, before dataset integration. Reviewers should check both dataset pages against the loader output and inspect the missing-file message in a browser. The assistant's own browser inspection was unavailable in this environment.
