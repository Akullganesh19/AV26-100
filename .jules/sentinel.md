## 2024-05-24 — Privilege Escalation in User Registration
**Found:** Mass assignment vulnerability in the `/register` endpoint allowing users to pass `role="admin"` in the payload and create an admin account.
**Why it existed:** The `UserCreate` Pydantic schema inherited from `UserBase` which exposed the `role` field directly to client input, and the route handler blindly trusted this input.
**Fix:** Explicitly hardcoded `role=UserRole.OFFICER` in the route handler and removed `role` and `is_active` from the base schema to prevent mass assignment.
**Learning:** Never trust client input for sensitive fields like roles or active flags. Always explicitly override these with safe defaults on the server side during creation.
**Watch for:** Other endpoints (like update user) that might use similar base schemas that expose sensitive fields.
