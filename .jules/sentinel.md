## 2026-10-08 — Privilege Escalation in User Registration
**Attacked:** `/api/v1/auth/register` endpoint
**Found:** The endpoint allowed an unauthenticated attacker to set their own role to `sysadmin` via the JSON payload.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Hardcoded `role=UserRole.OFFICER` during user creation, ignoring any role provided in the payload.
**Systemic pattern:** The `UserCreate` Pydantic schema inherited from `UserBase`, which exposed the `role` field. Watch for other endpoints that accept Pydantic schemas inheriting from base schemas containing privileged fields, especially in creation or update routes (e.g., `UserUpdate`).
