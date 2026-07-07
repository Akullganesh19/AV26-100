## 2025-02-14 — Critical token revocation bypass and systemic info leakage

**Found:** Token revocation check (`deps.get_current_user`) could be bypassed if Redis was unavailable, because it caught `Exception` and fell through to standard validation. Additionally, various routes in `clinical.py`, `predict.py`, and `districts.py` leaked raw exception strings (`str(e)`) to the client.

**Why it existed:** The `except Exception: pass` block in `deps.py` was likely intended to gracefully handle the fact that Redis revocation checks are a "nice-to-have" add-on to stateless JWT validation. However, catching *all* exceptions also caught explicitly raised `HTTPException`s from within the same `try` block, nullifying the revocation entirely. The information leakage was likely due to standard development practices not being hardened for production.

**Fix:** Modified `backend/app/api/deps.py` to specifically re-raise `HTTPException`s and explicitly fail closed on `redis.exceptions.RedisError`. Replaced all `detail=str(e)` occurrences in API routes with generic messages, backing them with `logger.exception()` for internal visibility.

**Learning:** When layering stateful checks (Redis blocklist) over stateless auth (JWT), failing open on infrastructure errors is dangerous. Catching raw `Exception` in authentication flows is a critical anti-pattern that hides logic bugs. `jwt.get_unverified_claims` from `python-jose` is the intended way to parse JWT without signature verification (replacing it with `jwt.decode` with disabled checks throws missing key error).

**Watch for:** Other places where generic `except Exception:` blocks might swallow intended control flow (like `raise HTTPException`).
