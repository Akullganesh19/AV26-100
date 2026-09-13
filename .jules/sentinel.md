## 2024-05-24 - Secure Deserialization and TOCTOU Prevention
**Vulnerability:** Time-of-Check-to-Time-of-Use (TOCTOU) vulnerability during model loading, compounded by use of non-existent `joblib.loads()`.
**Learning:** Checking a file's hash in memory and then reloading it from disk allows an attacker to swap the file between check and use.
**Prevention:** Always deserialize the exact byte buffer (`io.BytesIO(content)`) that was verified in memory, rather than re-reading the file from disk.
