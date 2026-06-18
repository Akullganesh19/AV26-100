## 2026-06-17 — Sentinel Journal

**Attacked:** Backend Exception Handling in API routes (`districts.py`, `clinical.py`, `predict.py`)
**Found:** Code failed open. Caught generic Exceptions (`except Exception as e:`) and directly bubbled up `str(e)` to HTTP 500 response details. This leaks internal stack traces and environment states, providing an attacker with valuable reconnaissance data.
**Severity:** 🔴 Exploitable now
**Fixed or flagged:** Fixed. Replaced bare exception responses with safe loggings using `logging.getLogger(__name__).error(..., exc_info=True)` and generic `Internal Server Error` messages.
**Systemic pattern:** This is a common pattern when developers use `try-except Exception` to handle unforeseen errors but overlook the security implications of echoing internal errors.

**Attacked:** JWT Token Revocation flow in `deps.py`
**Found:** Token validation failed open on infrastructure issues. If the backend failed to reach Redis (`redis.RedisError`), the revocation check was caught by a generic `except Exception:` block and "passed through", inadvertently granting access to potentially revoked tokens instead of failing closed.
**Severity:** 🔴 Exploitable now
**Fixed or flagged:** Fixed. Explicitly caught `redis.RedisError` and mapped it to a 500 internal server error, failing closed. Also caught other generic exceptions and let them fall through to the standard JWT signature validation to fail accurately.
**Systemic pattern:** Authentication and authorization systems should always fail closed. Catching generic exceptions around distributed checks often leads to security bypasses.

**Attacked:** Batch Inference in `prediction_service.py` (`predict_batch`)
**Found:** The `predict_batch` method launched multiple `predict_single` queries concurrently using `asyncio.gather(*tasks)` sharing a single SQLAlchemy `AsyncSession`. Since `AsyncSession` is strictly thread-local/task-local and does not support concurrent execution within the same transaction/session state, this led to `IllegalStateChangeError` crashes under concurrent load.
**Severity:** 🔴 Exploitable now (Denial of Service/Crashes under moderate usage)
**Fixed or flagged:** Fixed. Transformed the `predict_batch` task gathering into a sequential loop iterator, conforming to SQLAlchemy's async constraints.
**Systemic pattern:** Developers often mistakenly treat `asyncio.gather` as a drop-in concurrent executor without realizing the state-sharing constraints of underlying drivers or ORMs.
