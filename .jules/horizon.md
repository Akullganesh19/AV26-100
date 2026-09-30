## 2026-09-30 — Replace python-jose with PyJWT
**Risk identified:** python-jose is unmaintained and relies on legacy crypto which will become a problem.
**Migration target:** Modern, actively maintained PyJWT.
**Migrated this session:** Replaced python-jose with PyJWT for all JWT token validation/extraction.
**Remaining:** Passlib is another legacy crypto library for passwords to replace.
**Next session:** Migrate passlib to bcrypt or argon2-cffi.
