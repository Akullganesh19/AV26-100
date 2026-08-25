## 2026-06-16 — Security and Concurrency Vulnerabilities Patched
**Attacked:** Authentication middleware (`get_current_user`) and District prediction batching (`predict_batch`).
**Found:** 1) The auth middleware checked for revoked tokens but inadvertently swallowed the `HTTPException`, allowing revoked tokens full access. 2) The `predict_batch` function attempted concurrent `AsyncSession` database calls via `asyncio.gather`, causing `IllegalStateChangeError` crashes due to lack of thread-safety.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Re-raised `HTTPException` in token validation. Serialized district predictions loop.
**Systemic pattern:** Look for broad `try...except Exception:` blocks around auth flows and improper `asyncio.gather` on single DB sessions across the codebase.
