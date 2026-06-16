## 2024-06-16 — Fix Insecure Deserialization and Fail-Open Auth

**Found:**
1. Insecure Deserialization in `ClinicalService`: Machine learning scalers were loaded using `joblib.load()` without hash verification.
2. Broken Auth / Security Bypass in `get_current_user`: The Redis revocation check swallowed all exceptions, meaning if Redis was down, token revocation was bypassed entirely (failing open).

**Why it existed:**
1. Deserialization: Hash validation was implemented for the main predictive models but omitted for auxiliary artifacts (scalers). A partial fix created a false sense of security.
2. Auth: An overly broad `except Exception:` block was used to catch JWT parsing errors, inadvertently catching Redis connection errors as well.

**Fix:**
1. Extended the hash verification logic in `_verify_and_load` to apply to scalers as well, and added expected scaler hashes to the `manifest.json`.
2. Changed the exception handling in `deps.py` to explicitly catch `jwt.JWTError` for token issues and fail closed (HTTP 500) on general exceptions like Redis connection failures.

**Learning:**
- Partial validation of artifacts in a pipeline is insufficient; all components (including scalers/encoders) must be cryptographically verified before deserialization.
- Beware of overly broad `except Exception:` blocks in authentication middleware, as they frequently lead to fail-open vulnerabilities. Always specify the exact exception types expected.

**Watch for:**
- Other uses of `joblib.load` or `pickle.loads` that might bypass the manifest check (e.g., in new ML pipelines).
- Other instances where external dependencies (like DBs or caches) are used in security checks with generic exception handling.
