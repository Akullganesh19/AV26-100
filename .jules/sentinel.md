## 2024-03-24 — Systemic Exception Swallowing and Privilege Escalation
**Found:**
1. `except Exception:` blocks swallowing critical explicit `HTTPException` rules, causing fails-open on Redis errors or revoked tokens.
2. Privilege escalation via mass assignment (`user_in.role`) during user registration.
3. Information leakage (`str(e)`) in HTTP error responses.
**Why it existed:**
1. A broad `except Exception:` block meant to catch generic token validation errors was placed too broadly and ended up catching intentionally raised `HTTPException` responses, effectively disabling token revocation checks.
2. Direct object mapping from Pydantic input models to SQLAlchemy ORM models without explicit exclusions.
3. Rapid development practice of surfacing original exception messages during debugging.
**Fix:**
1. Explicitly caught `jose.exceptions.JWTError` for token validation bypassing, and `redis.RedisError` for fail-closed fallback. Allowed `HTTPException` to correctly propagate up.
2. Hardcoded `role=UserRole.OFFICER` server-side during registration.
3. Replaced `str(e)` in endpoint exception handlers with generic messages and logged exact exceptions internally.
**Learning:**
Always review `except Exception:` blocks for unintended security consequences, especially around authentication middleware. Never trust client-provided roles in signup payloads.
**Watch for:**
Other endpoints explicitly relying on broad try/except to catch predictable operational errors like connection failures or external service timeouts. Any new user models taking `dict(**kwargs)` inputs.
