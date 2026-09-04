## 2024-05-24 — Fail-Open Token Revocation Check
**Found:** Broad `except Exception:` block masking HTTPException in token revocation cache lookup.
**Why it existed:** Attempt to gracefully handle Redis connection failures during auth.
**Fix:** Explicitly catch and re-raise `HTTPException` before falling back. Used `jwt.JWTError` for token decoding to prevent masking system errors as token errors.
**Learning:** Broad exception handlers in auth paths that can intentionally raise HTTPExceptions will inadvertently "fail open" and bypass security checks (like token revocation) if the explicit exception isn't re-raised first.
**Watch for:** Other caching or fallback mechanisms wrapping auth logic using broad `except Exception:` handlers.
