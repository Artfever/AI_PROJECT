# P07-T3 deployment preparation

Issue [#245](https://github.com/Artfever/FleetpulseAI/issues/245) remains open.
No remote app, deployed commit, or remote parity result has been verified yet.

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

**Outstanding:** no reviewed mechanism currently supplies NASA FD001 input
histories to a remote checkout. They are ignored by Git. The only packaged
history is a clearly artificial example; it cannot
demonstrate the P07 real-data gate. Deployment is not complete merely because a
Streamlit health endpoint responds. Do not train at app startup or use the
official test answers to work around missing files. Agree a secure model
provisioning path and review the provenance and redistribution of any real-data
demo before a public deployment uses it. A checksum alone does not make a
serialized model trustworthy.

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

After provisioning and deployment, select the same data source, engine and
cycle remotely and record each observed display, warning, URL, commit and model
version. The UI rounds to two decimals; compare the displayed values above and
retain raw values separately for any service-level comparison. If input, model,
or software version differs, report it rather than claim parity.
