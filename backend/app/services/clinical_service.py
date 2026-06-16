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
MODELS_DIR = BACKEND_ROOT / "app" / settings.CLINICAL_MODELS_DIR

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

    def _verify_and_load(self, name: str, path: Path, expected_hash: Optional[str] = None):
        if not path.exists():
            raise FileNotFoundError(f"Model {name} not found at {path}")
        
        if expected_hash is None:
            expected = self._manifest["active"].get(name, {})
            expected_hash = expected.get("sha256")
        
        if not expected_hash:
            raise SecurityError(f"No hash defined for {name} in manifest!")

        with open(path, "rb") as f:
            content = f.read()
            actual_hash = hashlib.sha256(content).hexdigest().upper()
            if actual_hash != expected_hash.upper():
                raise SecurityError(f"Integrity violation: {name} model hash mismatch! Security compromised.")
            
            return joblib.loads(content)

    def _load_model(self, disease: str):
        if disease not in self._models:
            metadata = self._manifest["active"].get(disease)
            if not metadata:
                raise ValueError(f"Disease {disease} not supported in active manifest.")
            
            self._models[disease] = self._verify_and_load(disease, MODELS_DIR / metadata["file"])
            
            scaler_path = MODELS_DIR / f"scaler_{disease}.sav"
            if scaler_path.exists():
                scaler_hash = metadata.get("scaler_sha256")
                # 🛡️ Sentinel: Deserialization fix
                # Verify scaler hash before insecure deserialization (joblib/pickle)
                self._scalers[disease] = self._verify_and_load(f"scaler_{disease}", scaler_path, expected_hash=scaler_hash)
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

    def predict_heart(self, features: List[float]) -> Dict[str, Any]:
        self._load_model("heart")
        arr = np.array(features).reshape(1, -1)
        if self._scalers["heart"]:
            arr = self._scalers["heart"].transform(arr)
        
        try:
            prob = self._models["heart"].predict_proba(arr)[0][1]
        except AttributeError:
            prob = float(self._models["heart"].predict(arr)[0])
            
        return self._build_response("heart", prob)

    def predict_diabetes(self, features: List[float]) -> Dict[str, Any]:
        self._load_model("diabetes")
        arr = np.array(features).reshape(1, -1)
        if self._scalers["diabetes"]:
            arr = self._scalers["diabetes"].transform(arr)
        
        try:
            prob = self._models["diabetes"].predict_proba(arr)[0][1]
        except AttributeError:
            prob = float(self._models["diabetes"].predict(arr)[0])
            
        return self._build_response("diabetes", prob)

    def predict_parkinsons(self, features: List[float]) -> Dict[str, Any]:
        self._load_model("parkinsons")
        arr = np.array(features).reshape(1, -1)
        if self._scalers["parkinsons"]:
            arr = self._scalers["parkinsons"].transform(arr)
        
        try:
            prob = self._models["parkinsons"].predict_proba(arr)[0][1]
        except AttributeError:
            prob = float(self._models["parkinsons"].predict(arr)[0])
            
        return self._build_response("parkinsons", prob)

class SecurityError(Exception):
    pass
