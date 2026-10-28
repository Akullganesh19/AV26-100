## 2026-10-28 - [Swallowed Security Exceptions]
**Vulnerability class:** Exception swallowing in security critical logic.
**Entry point:** Token revocation check in get_current_user dependency.
**Fix:** Catch and re-raise explicit security-related exceptions (e.g., `except HTTPException: raise`) before a broader catch-all block.
**Blast radius before fix:** Authentication bypass via revoked tokens.
**Next opportunity:** Audit other try/except blocks in security dependencies.
