## 2026-06-16 — Rate Limit Bypass via JWT Sub Forging
**Attacked:** Unauthenticated endpoints (especially auth routes with `@limiter.limit`) via `get_user_id` in `backend/app/api/deps.py`.
**Found:** The `get_user_id` function extracts the `sub` claim from the JWT *without verifying the signature* using `jwt.get_unverified_claims`. An attacker can bypass IP-based rate limiting on sensitive endpoints (like login/register) by sending forged JWTs with random `sub` values. Each forged request is treated as a unique user and circumvents IP tracking.
**Severity:** 🔴 Exploitable now
**Fixed or flagged:** Fixed. Replaced the unverified JWT claim extraction in `get_user_id` with an IP-only fallback for unauthenticated routes. Once verified, the token logic shouldn't be used just for pre-auth rate limits. Wait, actually, let's fix it by only rate-limiting by IP for unauthenticated requests and pre-auth endpoints, or using the verified `sub` if a verified user dependency is met. The easiest fix is just returning IP unless we actually verify the token (which `get_user_id` doesn't do). So `get_user_id` should just return the IP for rate limits, OR we verify it if it's a known endpoint. Wait, rate limits run before auth dependency. It's safer to always use IP for public endpoints, or use IP for unverified requests.
**Systemic pattern:** Trusting unverified JWT claims (`get_unverified_claims`) for critical logic (like identity, rate limiting, or early checks).

## 2026-06-16 — Privilege Escalation via Mass Assignment in Registration
**Attacked:** `POST /api/v1/auth/register` in `backend/app/api/routes/auth.py`.
**Found:** The `UserCreate` schema inherits `role` from `UserBase` (which defaults to `OFFICER`). An attacker can explicitly include `"role": "admin"` or `"role": "sysadmin"` in the JSON payload. The registration endpoint blindly passes `user_in.role` to the new `User` model, granting the attacker instant admin privileges on account creation.
**Severity:** 🔴 Exploitable now
**Fixed or flagged:** Fixed. Hardcoded the role to `UserRole.OFFICER` during user creation regardless of what is passed in `user_in`, and ideally we would remove `role` from `UserCreate` (but hardcoding is safest).
**Systemic pattern:** Mass assignment / overposting vulnerabilities where Pydantic schemas allow inputs for fields that should be read-only or server-managed (like `role`, `is_active`).
