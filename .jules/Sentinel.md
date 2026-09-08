## 2024-05-24 - [Preventing TOCTOU in joblib deserialization]
**Vulnerability:** TOCTOU risk and invalid code when trying to deserialize verified joblib files in memory.
**Learning:** `joblib.loads()` does not exist for deserializing bytes in memory. Re-reading from disk via `joblib.load(path)` after hash verification introduces a Time-of-Check-to-Time-of-Use (TOCTOU) vulnerability where the file can be modified between the check and the load.
**Prevention:** Use `joblib.load(io.BytesIO(content))` to securely load the verified byte content directly from memory.
