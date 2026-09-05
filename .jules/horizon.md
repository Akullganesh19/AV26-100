## 2024-05-18 — Migrate python-jose to PyJWT
**Risk identified:** python-jose is no longer actively maintained, leading to potential security vulnerabilities and compatibility issues over time.
**Migration target:** PyJWT, which is actively maintained, widely adopted in the Python ecosystem, and securely handles modern cryptographic standards.
**Migrated this session:** Swapped python-jose for PyJWT in requirements and migrated authentication logic in app/core/security.py and app/api/deps.py. Handled JWT decode validation bypass and exception handling correctly.
**Remaining:** Complete migration of any remaining loose python-jose mentions if they exist.
**Next session:** Check if other microservices or dependent components also need their JWT libraries migrated.
