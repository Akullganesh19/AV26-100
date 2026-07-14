## 2024-05-18 — Mass Assignment Privilege Escalation in User Registration
**Attacked:** User registration endpoint (`POST /register` in `backend/app/api/routes/auth.py`)
**Found:** The `UserCreate` Pydantic model directly passed all fields, including `role` and `is_active`, directly to the `User` creation method. This mass assignment vulnerability allowed any new user to register with `role="admin"` and bypass all intended privilege checks, instantly becoming an administrator.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Hardcoded `role=UserRole.OFFICER` and `is_active=True` during the `User` instantiation in the `register` route, mitigating the risk. A static AST regression test was also run to ensure it persists.
**Systemic pattern:** Similar vulnerabilities could exist in other endpoints creating or updating database records from user-supplied models (e.g., PUT/PATCH paths on user profiles).
