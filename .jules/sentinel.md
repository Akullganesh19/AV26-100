## 2026-06-16 — [Auth Token Revocation Bypass & Batch Inference N+1]
**Attacked:** JWT Token Verification (`get_current_user`), Batch Inference (`predict_batch`)
**Found:**
1. The token revocation check in `get_current_user` swallowed `HTTPException` via a broad `except Exception:` block, allowing revoked tokens to bypass validation.
2. `predict_batch` executed an N+1 pattern by computing predictions for all districts concurrently without checking the `Prediction` database cache first.
**Severity:** 🔴 / 🟡
**Fixed or flagged:**
- The Auth bypass (🔴) was fixed. Added `except HTTPException: raise` to `deps.py`.
- The Batch Inference N+1 (🟡) was flagged for human review.
**Systemic pattern:** Broad exception handling in auth code is prone to swallowing intentional rejections. Check all Redis caching/idempotency guards for similar fail-closed handling.

## 🛡️ Adversarial Verification Report

**Scope attacked:** Auth Token Verification (`get_current_user`), Batch Inference (`predict_batch`)
**🔴 Exploitable findings:** None remaining.
**🟡 Latent findings:**
**Issue:** N+1 Database queries in `predict_batch`
**Severity:** 🟡
**Reproduction:** Call the `GET /api/v1/districts/` endpoint with 100+ districts.
**Impact:** The `PredictionService.predict_batch` function spawns 100 concurrent tasks that execute heavy ML inference and database writes, ignoring any existing cached predictions for the requested date and model version. This exhausts CPU and DB connection pools unnecessarily on read-heavy dashboards.
**Suggested direction:** Modify `predict_batch` to first query `Prediction` using an `in_()` clause for the requested `district_ids`. Map the results, and only spawn `_predict_with_sem` tasks for districts that are not found in the cache.

**🟢 Theoretical findings:** None this session.
**Fixed this session:**
- `get_current_user` swallowed `HTTPException` for revoked tokens (regression test added in `tests/security/test_deps.py`).
- CI `conftest.py` appended `_test` repeatedly on re-runs.
**Requires human review:**
- The `predict_batch` N+1 optimization needs a human engineer to review and implement the caching layer without causing data regression (e.g., dropping `baseline_score`).
- The local `auth/login` endpoint returns HS256 tokens while the rest of the application strictly validates against Clerk RS256. This architectural discontinuity needs review.
