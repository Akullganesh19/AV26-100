## 2026-06-16 — [Auth Token Revocation Bypass & Batch Inference N+1]
**Attacked:** JWT Token Verification (`get_current_user`), Batch Inference (`predict_batch`)
**Found:**
1. The token revocation check in `get_current_user` swallowed `HTTPException` via a broad `except Exception:` block, allowing revoked tokens to bypass validation.
2. `predict_batch` executed an N+1 pattern by computing predictions for all districts concurrently without checking the `Prediction` database cache first.
**Severity:** 🔴 / 🟡
**Fixed or flagged:** Fixed. Added `except HTTPException: raise` to `deps.py`. Added cache retrieval and merged results in `predict_batch` to avoid redundant ML inferences.
**Systemic pattern:** Broad exception handling in auth code is prone to swallowing intentional rejections. Check all Redis caching/idempotency guards for similar fail-closed handling.
