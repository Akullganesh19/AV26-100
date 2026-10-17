## 2024-10-18 - Fix insecure deserialization in scaler loading
**Vulnerability class:** Insecure Deserialization
**Entry point:** `backend/app/services/clinical_service.py` -> `_load_model`
**Fix:** Explicitly verified the SHA-256 hash of scaler files (`joblib.loads()`) against the manifest before deserialization.
**Blast radius before fix:** Maliciously crafted `.sav` scaler files could execute arbitrary code when loaded.
**Next opportunity:** Review other `.sav` or `pickle` loadings in ML pipelines (e.g., `prediction_service.py`) for missing hash checks.
