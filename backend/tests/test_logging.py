import logging
import sys
import io
import json
import pytest
from app.core.logging import setup_logging

def test_pii_redaction():
    setup_logging()

    root_logger = logging.getLogger()
    log_capture_string = io.StringIO()
    handler = logging.StreamHandler(log_capture_string)

    original_handler = None
    for h in root_logger.handlers:
        if isinstance(h, logging.StreamHandler) and h.stream == sys.stdout:
            original_handler = h
            break

    if original_handler:
        handler.setFormatter(original_handler.formatter)

    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    test_logger = logging.getLogger("test_redaction")

    test_logger.info(
        "User action performed",
        extra={
            "email": "testuser@example.com",
            "clerk_id": "user_213",
            "password": "secret_password",
            "public_id": "abcd123",
            "nested": {
                "SSN": "123-45-678",
                "phone": "555-555-5555"
            }
        }
    )

    test_logger.error("Failed to send email to user@domain.com due to timeout")

    log_contents = log_capture_string.getvalue().strip().split("\n")

    assert len(log_contents) >= 2

    log1 = json.loads(log_contents[0])
    assert log1["event"] == "User action performed"
    assert log1.get("email") == "[REDACTED]"
    assert log1.get("clerk_id") == "[REDACTED]"
    assert log1.get("password") == "[REDACTED]"
    assert log1.get("public_id") == "abcd123"
    assert log1.get("nested", {}).get("SSN") == "[REDACTED]"
    assert log1.get("nested", {}).get("phone") == "[REDACTED]"

    log2 = json.loads(log_contents[1])
    assert log2["event"] == "Failed to send email to [REDACTED_EMAIL] due to timeout"
