"""Stage an explicitly supplied trusted model for one prediction request."""

import base64
import binascii
from collections.abc import Mapping
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from fleetpulse.models.tree_artifact import MANIFEST_FILENAME, MODEL_FILENAME
from fleetpulse.services import PredictionArtifactError

MAX_ENCODED_BYTES = 2_000_000


@contextmanager
def prediction_manifest(local_manifest: Path, supplied_bundle: Mapping | None):
    """Use a local manifest or stage owner-provided base64 bytes temporarily.

    The prediction service still verifies artifact integrity and compatibility.
    Only trusted bundles should be supplied: checksums cannot establish trust.
    """
    if local_manifest.exists() or supplied_bundle is None:
        yield local_manifest
        return
    try:
        manifest_text = supplied_bundle["manifest_base64"]
        model_text = supplied_bundle["model_base64"]
        if not all(
            isinstance(value, str) and 0 < len(value) <= MAX_ENCODED_BYTES
            for value in (manifest_text, model_text)
        ):
            raise ValueError("Invalid encoded artifact length or type")
        manifest_bytes = base64.b64decode(manifest_text, validate=True)
        model_bytes = base64.b64decode(model_text, validate=True)
    except (KeyError, TypeError, ValueError, binascii.Error) as error:
        raise PredictionArtifactError("Invalid deployment model configuration.") from error

    try:
        with TemporaryDirectory(prefix="fleetpulse-model-") as directory:
            path = Path(directory)
            (path / MANIFEST_FILENAME).write_bytes(manifest_bytes)
            (path / MODEL_FILENAME).write_bytes(model_bytes)
            yield path / MANIFEST_FILENAME
    except OSError as error:
        raise PredictionArtifactError("Cannot stage the supplied deployment model.") from error
