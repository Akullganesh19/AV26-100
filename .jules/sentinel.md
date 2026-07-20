## 2025-07-20 — Mass Assignment in Registration
**Found:** User registration route permitted users to manually define `role`, `is_active`, and `alert_threshold` during account creation via `UserCreate` schema.
**Why it existed:** The `UserCreate` schema directly inherited from `UserBase` which contained all fields including internal flags, allowing users to bypass the intended default assignment and escalate their own privileges (e.g. setting `role=admin`).
**Fix:** Removed internal state fields from `UserBase` and `UserCreate`/`UserUpdate` schemas. Explicitly hardcoded the default initialization `role=UserRole.OFFICER` within the route handler logic.
**Learning:** Never inherit generic API response schemas (like `UserBase`) into input schemas (`UserCreate`) if they contain internal or privileged fields. Schema separation is crucial.
**Watch for:** Other endpoints parsing raw dicts into models or updating objects where schemas might expose fields like `id`, `is_active`, or internal status fields.

## 2025-07-20 — Information Leakage via Raw Exceptions
**Found:** Broad `except Exception as e:` blocks across almost all backend API routes returned `str(e)` directly to the user in HTTP 500 error responses (e.g. `/clinical/heart`, `/predict`, `/districts`).
**Why it existed:** Quick error handling pattern that favored developer convenience over safe failure design.
**Fix:** Modified exception handlers to log the full exception (`logger.error(..., exc_info=True)`) and raise `HTTPException` with a generic, user-safe error message (e.g., `"Internal Server Error"`).
**Learning:** API boundaries must act as a filter. Internal errors should never leak stack traces or raw exception messages, which could expose underlying system paths or database internals to an attacker.
**Watch for:** New endpoints utilizing generic try/catch blocks.

## 2025-07-20 — Path Traversal in Report Generation
**Found:** The `/api/reports` endpoint used a user-controlled parameter (`report_req.get('district_id')`) directly in the `Content-Disposition` filename string without any sanitization.
**Why it existed:** Trusting client input for file generation without considering injection attacks.
**Fix:** Stripped slashes and backslashes from the user input before interpolating it into the filename.
**Learning:** Always treat user input as hostile, especially when it interacts with the file system or HTTP headers.
**Watch for:** Any other endpoints generating files or accepting file paths as parameters.

## 2025-07-20 — Insecure JWT Validation Fallback
**Found:** The dual JWT validation logic (Clerk and local fallback) in `deps.get_current_user` was relying on a broad `except Exception:` to handle validation errors and fallback mechanisms. If Redis connection failed, or another unexpected error occurred during extraction, it could swallow the error and proceed or fail open.
**Why it existed:** Attempting to gracefully support two token types led to imprecise error catching, unintentionally catching infrastructure errors as validation failures.
**Fix:** Refactored the exception handling to catch specific JWT parsing errors (`jose_exceptions.JWTError`) and Redis errors separately, ensuring the auth system fails closed on infrastructure errors and explicitly returns 401/403/500 correctly.
**Learning:** Authentication mechanisms must fail closed. Never use broad exception handling when verifying credentials, as it can hide systemic failures.
**Watch for:** Other custom authentication dependencies or validation logic across external services.

## 2025-07-20 — XSS in Geospatial Tooltips
**Found:** The Leaflet map component in `StrategicMap.tsx` used string interpolation to inject raw user-controlled data (`district.name`, `risk_tier`, etc.) directly into an HTML template (`layer.bindTooltip(...)`).
**Why it existed:** Generating complex dynamic HTML structures for map tooltips without React's built-in JSX escaping.
**Fix:** Implemented and applied a manual `escapeHtml` sanitizer function to all user-provided strings before they are injected into the raw HTML template.
**Learning:** When bypassing React's DOM rendering (e.g. interfacing with imperative libraries like Leaflet or D3), XSS protections must be manually re-applied.
**Watch for:** `dangerouslySetInnerHTML`, `innerHTML`, and third-party imperative UI libraries.
