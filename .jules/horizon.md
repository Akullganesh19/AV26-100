## 2024-06-23 — python-jose and passlib deprecation migration
**Risk identified:** `python-jose` and `passlib` are unmaintained/deprecated and pose a security and functional risk over the next few years due to lacking updates, standard breakages (e.g., passlib `AttributeError: module 'bcrypt' has no attribute '__about__'`), and general community abandonment.
**Migration target:** The modern and actively maintained `PyJWT` for JWT handling, and using the `bcrypt` API directly for secure password hashing.
**Migrated this session:** The core auth implementations in `backend/app/core/security.py` and API auth dependency injection (`backend/app/api/deps.py`), replacing both libraries with PyJWT and direct bcrypt.
**Remaining:** The main auth routing and logic have been migrated.
**Next session:** Identify and migrate other uses of abandoned dependencies if any exist.
