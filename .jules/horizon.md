## 2025-02-14 — PyJWT Migration
**Risk identified:** The backend uses `python-jose`, which has been abandoned for several years and lacks support for newer Python versions and cryptography updates. Its latest version (3.3.0) is pinned and causes compatibility issues moving forward. The ecosystem has overwhelmingly moved to `PyJWT`.
**Migration target:** `PyJWT` (specifically `PyJWT[crypto]` for RSA support).
**Migrated this session:** Replace `python-jose` with `PyJWT` in backend dependencies (`requirements.txt`) and update all `jose` imports and method calls (`jwt.encode`, `jwt.decode`) across the codebase.
**Remaining:** None. This migration is self-contained.
**Next session:** Start looking into `passlib` which is also abandoned, or update the node packages.
