## 2026-10-20 — Mass Assignment in Registration
**Attacked:** User registration endpoint (`/api/v1/auth/register`)
**Found:** The `UserCreate` schema inherited from `UserBase`, which contained sensitive fields (`role`, `is_active`, `alert_threshold`). This allowed privilege escalation during registration.
**Why it existed:** Pydantic schema inheritance pattern where `Create` mistakenly inherited privileged properties from `Base`.
**Fix:** Created a new `UserRegister` schema inheriting from `BaseModel` explicitly listing only safe fields (`email`, `name`, `password`). Updated the register route to use this schema.
**Learning:** Never inherit `Create` or `Update` schemas used in public endpoints from `Base` schemas containing privileged fields.
**Watch for:** Other endpoints passing user input directly into model constructors without filtering.
