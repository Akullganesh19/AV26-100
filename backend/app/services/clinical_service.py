import pickle
import joblib
import numpy as np
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.core.config import settings

# Paths resolved relative to the backend root (where main.py runs)
BACKEND_ROOT = Path(__file__).parent.parent.parent
MANIFEST_PATH = BACKEND_ROOT / settings.CLINICAL_MANIFEST_PATH
MODELS_DIR = BACKEND_ROOT / settings.CLINICAL_MODELS_DIR

DISCLAIMER = (
    "Tactical screening tool only. Not a clinical diagnosis. "
    "Consult a licensed medical professional for all clinical decisions. "
    "Accuracy based on established clinical datasets."
)

class ClinicalService:
    def __init__(self):
        self._models = {}
        self._scalers = {}
        self._manifest = self._load_manifest()

    def _load_manifest(self):
        if not MANIFEST_PATH.exists():
             return {"active": {}}
        with open(MANIFEST_PATH, "r") as f:
            return json.load(f)

    def _verify_and_load(self, name: str, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"Model {name} not found at {path}")
        
        expected = self._manifest["active"].get(name, {})
        expected_hash = expected.get("sha256")
        
        if not expected_hash:
            raise SecurityError(f"No hash defined for {name} in manifest!")

        with open(path, "rb") as f:
            content = f.read()
            actual_hash = hashlib.sha256(content).hexdigest().upper()
            if actual_hash != expected_hash.upper():
                raise SecurityError(f"Integrity violation: {name} model hash mismatch! Security compromised.")

        return joblib.load(path)

    def _load_model(self, disease: str):
        if disease not in self._models:
            metadata = self._manifest["active"].get(disease)
            if not metadata:
                raise ValueError(f"Disease {disease} not supported in active manifest.")
            
            self._models[disease] = self._verify_and_load(disease, MODELS_DIR / metadata["file"])
            
            scaler_path = MODELS_DIR / f"scaler_{disease}.sav"
            if scaler_path.exists():
                self._scalers[disease] = joblib.load(scaler_path)
            else:
                self._scalers[disease] = None

    def _build_response(self, disease: str, prob: float) -> Dict[str, Any]:
        meta = self._manifest["active"][disease]
        return {
            "disease": disease,
            "risk_score": round(prob, 4),
            "risk_tier": "HIGH" if prob > 0.7 else "MEDIUM" if prob > 0.4 else "LOW",
            "risk": prob > 0.5,
            "advice": "Mandatory clinical follow-up required." if prob > 0.7 else "Normal observation.",
            "confidence_note": DISCLAIMER,
            "model_version": meta["version"],
            "trained_on": meta["trained_on"],
            "input_completeness": "FULL",
            "screened_at": datetime.utcnow().isoformat()
        }

    def predict(self, disease: str, features: List[float]) -> Dict[str, Any]:
        self._load_model(disease)
        arr = np.array(features).reshape(1, -1)
        if self._scalers[disease]:
            arr = self._scalers[disease].transform(arr)
        
        try:
            prob = self._models[disease].predict_proba(arr)[0][1]
        except AttributeError:
            prob = float(self._models[disease].predict(arr)[0])
            
        return self._build_response(disease, prob)

class SecurityError(Exception):
    pass
