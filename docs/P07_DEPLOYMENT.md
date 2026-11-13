# P07-T3 deployment preparation

Issue [#245](https://github.com/Artfever/FleetpulseAI/issues/245) remains open.
Taha reported the hosted results below match the local references. The deployed commit and the public-access discrepancy remain unverified; do not treat the phase gate as complete.

## Community Cloud configuration

The app entrypoint is `app/Home.py`; choose **Python 3.12**. The root
`requirements.txt` installs this project from `pyproject.toml`, including its
pinned runtime dependencies. Community Cloud installs and runs from a GitHub
checkout; local ignored files do not appear there. See Streamlit's
[dependency instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)
and [deployment instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).
Deploy an approved task branch for verification and later the phase-approved
branch, recording the actual branch, commit, URL and model version. Do not put
credentials in the repository or chat. The account owner signs in personally.

The owner can supply the existing trusted P06 model in Community Cloud app
secrets without committing it to Git. Run
`python scripts/prepare_p07_model_secrets.py` locally; this validates the local
bundle and creates the ignored file `reports/p07_streamlit_model_secrets.toml`
without overwriting an existing file. Paste its contents into the app's
**Advanced settings > Secrets** in Community Cloud, never into chat or Git.
The page uses a local bundle when present; otherwise, on an explicit prediction,
it temporarily stages the supplied model and manifest, then removes the staged
files. The existing service verifies their hashes and compatibility before
inference. This is not encryption or provenance verification: only provide a
bundle from a trusted source. Secret contents can include development evaluation
metadata and must not be published. No model is trained or downloaded at startup.

The repository owner approved a small real FD001/train subset for the public
demo on 13 November 2026. `scripts/package_p07_training_subset.py` verifies the
full local training-file SHA-256 before preserving only engines 4/164, 5/58,
and 12/7 prefixes (229 rows) in `data/demo/fd001_training_prefixes.txt`. The
app exposes it as **Packaged FD001/train parity subset**, clearly labeled as
truncated training histories for the three parity examples. It does not include
the full dataset, validation/test files, or RUL answers. The packed file's
SHA-256 is
`e31832ddbc23fa32b4093e1325f00fd6bed2cb2d3f6d03ca13ace44886390b6d`.

The source page does not state a dataset-specific redistribution license. This
records the project owner's decision to package a limited demonstration subset,
not a NASA license grant. Review `docs/data_policy.md` and
`docs/fd001_provenance.md` for provenance and scope. Deployment identity and anonymous access remain unverified; the
UI comparison is user-reported below. Deployment is not complete merely because a
Streamlit health endpoint responds. Do not train at app startup or use official
test answers. A checksum alone does not make a serialized model trustworthy.

## User-reported hosted observations

On 13 November 2026 Taha confirmed he selected **Packaged FD001/train parity
subset** in the hosted app at https://fleetpulseai.streamlit.app/, and observed
34.20, 158.16 and 184.36 cycles for engines/cycles 4/164, 5/58 and 12/7,
respectively, with the short-window warning for 12/7. He reported model
`decision-tree-rul` / `decision-tree-rul-v1`. These UI results match the local
display values below; no independent remote raw-output comparison is claimed.

Taha reports the deployed branch is `dev` and that the app opened without
sign-in in an incognito window. Cloud startup logs he supplied name `dev` but
not a deployed commit hash. The provided `44d3063` identifies an older P01
commit and cannot establish the running revision. Unauthenticated requests from
this environment returned HTTP 303 to Streamlit sign-in. Resolve that discrepancy
and record the deployed commit before representing #245 and the shared gate as
fully verified.
## Local reference predictions

On 13 November 2026, `.venv/Scripts/python.exe scripts/p07_local_reference.py`
read the local original simulated NASA FD001 training histories and the saved
development Decision Tree. The source SHA-256 was
`963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8`;
the saved model SHA-256 was
`2a693e6ecc09de5d9549e287a6798fdb339c7e945c700231444f0c5bcd425018`.
The model was `decision-tree-rul-v1`, scikit-learn 1.9.1, seed 42,
`past-only-v1` features, window 30, max depth 8, minimum leaf 5.

| FD001/train engine | Observed cycle | Raw local estimate (cycles) | UI display (cycles) | Warning |
| --- | ---: | ---: | ---: | --- |
| 4 | 164 | 34.19607843137255 | 34.20 | none |
| 5 | 58 | 158.16 | 158.16 | none |
| 12 | 7 | 184.35714285714286 | 184.36 | short window |

Each service call received only that engine's raw rows through the selected
cycle. No target was passed and no official test file was read. These are
development-model outputs, not accuracy metrics or maintenance advice.

The subset can be regenerated from a local original training file with
`python scripts/package_p07_training_subset.py`. Observed package: 229 rows,
three engines and SHA-256
`e31832ddbc23fa32b4093e1325f00fd6bed2cb2d3f6d03ca13ace44886390b6d`.

After provisioning and deployment, select the same data source, engine and
cycle remotely and record each observed display, warning, URL, commit and model
version. The UI rounds to two decimals; compare the displayed values above and
retain raw values separately for any service-level comparison. If input, model,
or software version differs, report it rather than claim parity.
