## 2024-05-24 - [Insecure Joblib Deserialization TOCTOU]
**Vulnerability:** Joblib deserialization TOCTOU issue. The code verified a file hash in memory (`f.read()`), but `joblib.loads()` does not exist so it would crash. If they had "fixed" it by doing `joblib.load(path)`, it would read the file from disk again, causing a Time-of-Check-to-Time-of-Use (TOCTOU) vulnerability where an attacker could swap the file on disk after verification but before loading.
**Learning:** Never verify file content in memory and then re-read the file path for the actual operation.
**Prevention:** Use `io.BytesIO` to wrap the already-verified bytes loaded in memory so that `joblib.load()` operates on the safely checked content.
