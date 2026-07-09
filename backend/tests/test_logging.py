import pytest
import logging
from unittest.mock import patch
import io
import json
from app.core.logging import setup_logging

def test_logging_redacts_pii():
    setup_logging()

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)

    # We need to get the actual formatter set up by setup_logging
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]

    try:
        # Assuming there is exactly one handler added by setup_logging
        formatter = root_logger.handlers[0].formatter
        handler.setFormatter(formatter)

        test_logger = logging.getLogger("test_redaction")
        test_logger.handlers = [handler]
        test_logger.propagate = False

        test_logger.info(
            "User registered",
            extra={
                "email": "hacker@example.com",
                "password": "supersecretpassword",
                "ssn": "999-99-9999",
                "vocal_metrics": [1.0, 2.0, 3.0],
                "safe_field": "hello"
            }
        )

        output = stream.getvalue()
        assert output

        log_entry = json.loads(output)
        assert log_entry["email"] == "h***@example.com"
        assert log_entry["password"] == "[REDACTED]"
        assert log_entry["ssn"] == "[REDACTED]"
        assert log_entry["vocal_metrics"] == "[REDACTED]"
        assert log_entry["safe_field"] == "hello"
        assert log_entry["event"] == "User registered"
    finally:
        root_logger.handlers = original_handlers
