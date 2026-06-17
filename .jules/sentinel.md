## 2023-10-27 — Security Audit and Hardening Sweep
**Found:**
1. Authentication failed open on Redis infrastructure errors (`backend/app/api/deps.py`).
2. Missing integrity checks for loaded scaler `.sav` models, introducing a risk of insecure deserialization (`backend/app/services/clinical_service.py`).
3. Verbose exception handling leaked internal state via stack trace dumps to clients (`backend/app/api/routes/clinical.py`, `backend/app/api/routes/predict.py`, `backend/app/api/routes/districts.py`).

**Why it existed:**
1. Blanket exception handling intended to catch missing or malformed JWT claims but unintentionally caught infrastructure-level HTTP errors.
2. Incomplete use of manifest features meant base models were hash-checked but scalers were left vulnerable.
3. Rapid development of API routes used basic `try/except` blocks returning `str(e)` without considering external visibility.

**Fix:**
1. Structured exception catching in `get_current_user` to fail closed natively and bubble up infrastructure errors securely.
2. Added scaler hashes to `backend/app/core/manifest.json` and reused `_verify_and_load` for scaler loading in `clinical_service.py`.
3. Masked server errors in `clinical.py`, `predict.py`, and `districts.py` by returning generic "internal error" messages while logging full exceptions locally.

**Learning:**
- Always ensure infrastructure failures (e.g. database, Redis connection issues) fail closed, especially around authentication or authorization checks.
- When applying hash verification to model artifacts, consider the entire pipeline (including scalers, transformers).
- Exception contents should never be returned to the client in HTTP 500 responses without being scrubbed.

**Watch for:**
- Other endpoints utilizing broad `Exception` catches.
- Additional artifacts loaded dynamically via `joblib` or `pickle` that may skip the manifest.
