## 2026-06-19 — Structural API Error Information Leakage
**Found:** Broad `except Exception as e:` blocks across Fast API routes were capturing generic and unexpected server errors and forwarding `str(e)` directly to the client via `HTTPException` detail fields.
**Why it existed:** Quick scaffolding of API routes favored verbosity in the client for debugging purposes without properly differentiating between user-facing errors and internal system stack traces/exceptions.
**Fix:** Refactored the `except Exception as e:` blocks across `main.py`, `predict.py`, `districts.py`, and `clinical.py` to use `logging.getLogger(__name__).error("...", exc_info=True)` to internally record the real error while raising an `HTTPException` with a generic, sanitized string.
**Learning:** Never leak internal infrastructure exceptions. All unhandled or unexpected exceptions should return a generic 500 error, and the real exception should be logged internally.
**Watch for:** New API routes implementing broad try/catch logic and embedding the exception string in the response detail.

## 2026-06-19 — Silent Authentication Fallback (Fail Open)
**Found:** The Redis-backed token revocation check in `get_current_user` inside `deps.py` caught all exceptions during the Redis lookup and silently passed, failing open if the Redis infrastructure was down or unreachable.
**Why it existed:** Likely implemented to ensure the service continued functioning even if the revocation cache briefly went down, prioritizing availability over strict security validation.
**Fix:** Modified the except block. Now, standard HTTP exceptions are re-raised, but internal connection or Redis errors are caught, logged, and trigger an HTTP 500 `Authentication infrastructure unavailable`.
**Learning:** Security validations, particularly authentication and token revocation, must fail closed. If the system cannot verify a token hasn't been revoked, it must reject the request.
**Watch for:** Other infrastructure dependencies in the authentication path (like JWKS fetching) silently failing and falling back to insecure defaults.

## 2026-06-19 — Insecure Deserialization of ML Scalers
**Found:** While ML models were securely loaded via `joblib` using an integrity check (`_verify_and_load`) against `manifest.json`, the accompanying `scaler_{disease}.sav` files were loaded directly using `joblib.load(scaler_path)` without any hash verification.
**Why it existed:** The manifest only tracked the core model weights, and scalers were likely treated as secondary data artifacts rather than executable payloads susceptible to insecure deserialization attacks.
**Fix:** Updated `manifest.json` to include `scaler_sha256` hashes for all models. Refactored `_verify_and_load` in `clinical_service.py` to accept an `expected_hash` parameter and updated `_load_model` to verify scalers using this secure pathway before deserialization.
**Learning:** Any file loaded using insecure deserialization mechanisms (like `pickle` or `joblib`) must be strictly cryptographically verified, regardless of whether it's a model, scaler, or supplementary configuration.
**Watch for:** New artifacts added to the prediction pipelines (e.g., in `prediction_service.py`) using `joblib.load` without hash verification.