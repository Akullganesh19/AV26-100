## 2026-03-16 — Migrate python-jose to PyJWT
**Risk identified:** python-jose is practically unmaintained, has known vulnerability risks, and depends on deprecated cryptography functions. It will become increasingly risky and hard to support.
**Migration target:** PyJWT, which is actively maintained, modern, and widely adopted for JWT handling in Python ecosystems.
**Migrated this session:** Replaced python-jose with PyJWT across the backend dependencies and core auth logic (security.py, deps.py). Handled options translation for decoding.
**Remaining:** None.
**Next session:** Look for other legacy dependencies or patterns that need modernization.
