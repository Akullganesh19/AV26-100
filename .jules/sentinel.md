## 2024-10-21 — Fix Mass Assignment and Swallowed HTTPExceptions
**Found:** Privilege escalation in user registration due to `UserCreate` inheriting `role` from `UserBase`, and token revocation bypass in `get_current_user` due to `except Exception` swallowing an intentional `HTTPException`.
**Why it existed:** Developers often reuse Pydantic base models without realizing they inherit privileged fields. Similarly, generic exception handlers are often added for resilience but can inadvertently catch and swallow intentionally raised HTTP exceptions like 401 Unauthorized.
**Fix:** Decoupled `UserCreate` from `UserBase` to drop sensitive inputs and explicitly set `UserRole.OFFICER` on the server side. Added an explicit `except HTTPException: raise` before generic `except Exception` handlers in FastAPI dependency overrides and route handlers.
**Learning:** Never inherit schema models for creation/updates from base schemas containing privileged fields. Always explicitly catch and re-raise `fastapi.HTTPException` before catching generic `Exception`s to prevent security bypasses.
**Watch for:** Other Pydantic schemas inheriting from models with sensitive fields, and other `try-except` blocks that might be swallowing `HTTPException`.

## 2024-10-21 — Fix database connection string bug in test suite
**Found:** Flawed logic for deriving the test database URL causes CI failure due to duplicated suffix.
**Why it existed:** Hardcoded string concatenation without checking the existing value of the database URL.
**Fix:** Strip trailing slashes and conditionally append `_test` only if the string does not already end with it.
**Learning:** In pytest `conftest.py` setups for SQLAlchemy, when creating a dedicated test database URL by appending `_test` to the application's `DATABASE_URL`, first strip trailing slashes (e.g., `.rstrip("/")`) before checking if the string already ends with `_test`.
**Watch for:** Other hardcoded string manipulations that assume specific input formats.
