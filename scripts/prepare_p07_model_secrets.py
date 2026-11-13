"""Create an ignored local TOML file for the owner to paste into Cloud secrets."""

import base64
import os

from fleetpulse import PROJECT_ROOT
from fleetpulse.models.tree_artifact import MANIFEST_FILENAME, MODEL_FILENAME
from fleetpulse.services.predictor import _load_model


def main():
    bundle_dir = PROJECT_ROOT / "artifacts/development"
    manifest = bundle_dir / MANIFEST_FILENAME
    model = bundle_dir / MODEL_FILENAME
    # Only run this on the owner's trusted local P06 bundle.
    _load_model(manifest)
    manifest_encoded = base64.b64encode(manifest.read_bytes()).decode("ascii")
    model_encoded = base64.b64encode(model.read_bytes()).decode("ascii")
    destination = PROJECT_ROOT / "reports/p07_streamlit_model_secrets.toml"
    destination.parent.mkdir(parents=True, exist_ok=True)
    text = (
        "[deployment_model]\n"
        f'manifest_base64 = "{manifest_encoded}"\n'
        f'model_base64 = "{model_encoded}"\n'
    )
    # Never overwrite another local file and do not print model bytes.
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as file:
        file.write(text)
    print(f"Prepared ignored local file: {destination.relative_to(PROJECT_ROOT)}")
    print("Paste its content into the app's Streamlit secrets, not into chat or Git.")


if __name__ == "__main__":
    main()
