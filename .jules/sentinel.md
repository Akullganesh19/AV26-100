## 2024-05-18 — Sentinel: Fixed Fail-Open Revocation & PII Leakage
**Found:**
1. Authentication vulnerability in `backend/app/api/deps.py` where token revocation checked against Redis was wrapped in a broad `except Exception: pass`, resulting in a fail-open state where explicit 401 exceptions for revoked tokens were caught and suppressed, allowing revoked tokens to bypass validation.
2. PII Leakage across several backend routes (`main.py`, `districts.py`, `predict.py`, `clinical.py`) where broad `except Exception as e:` blocks exposed `str(e)` directly to API consumers, risking the leakage of internal traces or Pydantic validation errors.

**Why it existed:**
1. The revocation check attempted to swallow token payload decoding exceptions safely using a broad catch, but inadvertently also swallowed the `raise HTTPException` statement and Redis infrastructure errors.
2. Fast iteration and copy-pasted boilerplate exception handling prioritized returning an error to the user over masking internal mechanisms.

**Fix:**
1. Replaced the generic exception handler with `except jwt.JWTError: pass` and `except redis.RedisError:` to raise a 500 error, explicitly failing closed on infrastructure error while allowing the 401 Unauthorized exception for revoked tokens to bubble up.
2. Changed `str(e)` to `type(e).__name__` or generic strings for client-facing HTTP exceptions across all identified files, preventing potential PII exposure.

**Learning:**
Broad exception handlers around authentication logic are extremely dangerous because they can easily swallow both verification failures and explicit rejection exceptions, causing fail-open behavior. Always explicitly handle specific errors (e.g., `jwt.JWTError`) and let infrastructure failures default to fail-closed. Exception messages must never surface `str(e)` to external consumers.

**Watch for:**
Future endpoints or middleware using `except Exception:` to silently ignore potential security checks or failing to sanitize error responses.
