import pytest
import json
import hashlib
from pathlib import Path
from unittest.mock import patch
from app.services.prediction_service import load_artifacts

def test_load_artifacts_integrity_check_failure(tmp_path):
    # Setup mock models directory and latest.json
    models_dir = tmp_path / "models"
    models_dir.mkdir()

    # Create fake joblib files
    files = {
        "pipeline": "fake_pipeline.joblib",
        "regressor": "fake_regressor.joblib",
        "classifier": "fake_classifier.joblib",
        "explainer": "fake_explainer.joblib"
    }

    hashes = {}
    for key, filename in files.items():
        file_path = models_dir / filename
        import joblib
        import io
        buf = io.BytesIO()
        joblib.dump("fake_model", buf)
        content = buf.getvalue()
        file_path.write_bytes(content)
        # Compute real hash
        real_hash = hashlib.sha256(content).hexdigest()
        hashes[key] = real_hash

    # Deliberately modify one hash to trigger integrity failure
    hashes["classifier"] = "badhash"

    manifest = {
        "version": "1.0",
        "pipeline": files["pipeline"],
        "regressor": files["regressor"],
        "classifier": files["classifier"],
        "explainer": files["explainer"],
        "hashes": hashes,
        "feature_bounds": {}
    }

    manifest_path = models_dir / "latest.json"
    manifest_path.write_text(json.dumps(manifest))

    # Patch the paths in prediction_service
    with patch("app.services.prediction_service.MODELS_DIR", models_dir):
        with patch("app.services.prediction_service.MANIFEST_PATH", manifest_path):
            with pytest.raises(RuntimeError) as exc_info:
                load_artifacts()

            assert "Security error: hash mismatch for classifier" in str(exc_info.value)
