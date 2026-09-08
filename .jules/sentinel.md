## 2026-06-16 — Revoked Token Bypass
**Found:** A revoked JWT token bypasses authentication because the explicit `HTTPException(401)` raised during the blocklist check is silently swallowed by a broad `except Exception: pass` block, causing the flow to fall through to standard token verification (fail-open).
**Why it existed:** The broad exception block was likely added to handle temporary Redis connection failures or missing `jti` claims, allowing standard verification to proceed if the blocklist was unreachable, but it inadvertently caught the intentional security halt.
**Fix:** Explicitly added `except HTTPException: raise` before the generic `except Exception` block to ensure intentional security halts are propagated correctly.
**Learning:** Security fail-open mechanisms must be precisely scoped; catching base `Exception` near security control flows routinely masks intentional errors and creates critical bypass vulnerabilities.
**Watch for:** Other fail-open authentication or dependency checks wrapped in generic `except Exception` handlers throughout FastAPI logic.
