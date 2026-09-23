## 2023-10-27 — Mass Assignment Vulnerability in Registration
**Found:** The `register` endpoint in `auth.py` blindly accepted the `role` field from the request body.
**Why it existed:** The `UserCreate` schema included `role` directly, and it was passed through without validation.
**Fix:** Hardcoded `role=UserRole.OFFICER` during user creation, ignoring the input.
**Learning:** Always explicitly set privileged fields rather than passing them through from request schemas.
**Watch for:** Other endpoints (like update user) might have the same vulnerability.
