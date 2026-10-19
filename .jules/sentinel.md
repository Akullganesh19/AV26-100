## 2024-10-19 — Mass Assignment Vulnerability in Registration
**Found:** `backend/app/api/routes/auth.py` allows mass assignment where a user can specify their own `role` and `is_active` status during registration due to inheriting fields from `UserBase`.
**Why it existed:** The `UserCreate` Pydantic schema inherits from `UserBase`, which includes sensitive fields like `role` and `is_active` without explicitly excluding them from user input.
**Fix:** Explicitly set safe defaults (`role=UserRole.OFFICER`, `is_active=True`) on the server side when instantiating the database model, overriding any client-provided values.
**Learning:** Never inherit `Create` or `Update` schemas from `Base` schemas containing privileged fields. Always explicitly drop sensitive inputs or enforce safe server-side defaults during model instantiation.
**Watch for:** Other endpoints using Pydantic inheritance that may inadvertently expose sensitive model fields to user modification.
