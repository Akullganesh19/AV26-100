## 2024-05-18 — Prevent Information Leakage in HTTP Responses
**Found:** Raw exception strings (`str(e)`) were being leaked in HTTP response details across multiple endpoints (`predict`, `clinical`, `districts`, `main`), exposing system internals.
**Why it existed:** It was a quick way to bubble up errors during development.
**Fix:** Masked internal errors with generic HTTP response details while ensuring the real exceptions are captured securely server-side using `logger.exception`.
**Learning:** Always separate user-facing error messages from internal logging traces to prevent attackers from mapping the system's infrastructure.
**Watch for:** Other endpoints passing raw database or infrastructure exceptions directly to the client.
