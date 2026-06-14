## 2025-05-21 - Information Exposure Through Error Messages
**Vulnerability:** API endpoints were returning raw exception strings (e.g., `str(e)`) in `HTTPException` details, which can leak stack traces, database schema details, or other sensitive internal information to attackers.
**Learning:** This pattern often emerges when developers prioritize debugging convenience over security, forgetting that error messages are part of the application's attack surface.
**Prevention:** Implement a strict policy of returning only generic, user-friendly error messages in client-facing responses. Use structured internal logging (e.g., `logger.error` or specialized audit logs) to capture full exception details for diagnostics.
