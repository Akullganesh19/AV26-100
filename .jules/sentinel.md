## 2024-05-24 — Fix Mass Assignment & Generic Error Swallowing
**Found:** Privilege escalation in user registration due to `role` inheritance in `UserCreate` schema, and global exception handlers swallowing deliberate `HTTPException` responses (e.g. rate-limiting, 401s).
**Why it existed:** Subclassing `UserBase` for registration conveniently included fields but unintentionally exposed `role` and `is_active`. Catch-all `except Exception` blocks were added to endpoints to prevent raw tracebacks but inadvertently caught FastAPIs HTTP exceptions too.
**Fix:** Decoupled `UserCreate` from `UserBase` to ensure sensitive fields are dropped. Added explicit `except HTTPException: raise` blocks before generic exception handlers across route files.
**Learning:** Pydantic inheritance can silently introduce mass-assignment risks if base models contain privileged fields. Exception handlers must always respect framework-specific intentional exceptions first.
**Watch for:** Other schemas inheriting from base classes with administrative fields, and generic `except Exception` blocks without preceding `HTTPException` catches.
