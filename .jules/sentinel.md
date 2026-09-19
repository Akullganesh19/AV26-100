## 2024-05-18 — Privilege Escalation in Registration
**Found:** The `POST /api/auth/register` endpoint allowed callers to supply their own role (e.g. `role: "admin"`) via the JSON body, which was blindly mapped to the newly created user in the database.
**Why it existed:** The `UserCreate` Pydantic schema included `role`, and the route handler mapped `user_in.role` straight to the DB model instantiation. This was likely done for convenience during early testing and not locked down for production.
**Fix:** Hardcoded `role=UserRole.OFFICER` directly in the database creation step in `auth.py`.
**Learning:** Always explicitly hardcode default, low-privilege roles on public registration endpoints regardless of what is allowed in the Pydantic schemas.
**Watch for:** Other endpoints (like update/edit profile) that might accept `role` updates.
