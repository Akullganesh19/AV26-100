## 2024-11-09 - Authorization Bypass in Auth Middleware
**Vulnerability:** A broad `except Exception:` block swallowed 401 Unauthorized `HTTPExceptions` thrown when a revoked token (checked via Redis) was detected.
**Learning:** Always catch explicitly raised `HTTPExceptions` and re-raise them before catching general `Exceptions` in FastAPI dependencies to avoid swallowing security-critical errors.
**Prevention:** Avoid generic `except Exception` blocks around security critical paths, or explicitly handle known exception types (like `HTTPException`) first.
