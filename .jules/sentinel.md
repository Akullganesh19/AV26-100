## 2025-07-15 — Privilege Escalation & Logging Bypass fixes
**Found:**
1. Privilege Escalation via Mass Assignment in `/register` endpoint (`backend/app/api/routes/auth.py`). The `UserCreate` schema included `role` and `is_active` fields, and the route allowed arbitrary injection, permitting new users to sign up as `UserRole.ADMIN` or `UserRole.SYSADMIN`.
2. Logging Configuration Bypass in `backend/app/core/config.py`. `logging.basicConfig()` was redundantly declared, overriding the centralized `structlog` configuration (including PII redaction) set up in `backend/app/main.py`.

**Why it existed:**
1. The `UserCreate` Pydantic model inherited `role` from `UserBase` for DRY principles but didn't restrict what could be provided during registration.
2. Standard practice of throwing `logging.basicConfig()` into config files for early debugging without realizing it conflicts with application-level structured logging.

**Fix:**
1. Hardcoded `role=UserRole.OFFICER` and `is_active=True` in the `/register` endpoint when instantiating the `User` object, overriding any provided input.
2. Removed `logging.basicConfig()` from `backend/app/core/config.py`, relying on `setup_logging()` in `backend/app/main.py`.

**Learning:**
1. Never trust client input for privilege fields, even if the Pydantic schema allows it. Always explicitly override security-sensitive fields server-side on entity creation.
2. Centralize logging configuration to a single startup script to ensure security features like PII redaction aren't accidentally bypassed.

**Watch for:**
1. Other instances where base Pydantic models with sensitive fields (e.g. `is_active`, `role`, `status`) are used for client input without strict server-side overrides.
2. Accidental re-configurations of logging in new modules or scripts.
