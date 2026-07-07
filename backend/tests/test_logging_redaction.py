import logging
from app.core.logging import setup_logging
import structlog
import sys

def test_redaction(capsys):
    setup_logging()

    # Test structural logging
    log = structlog.get_logger("test")
    log.info("user action", email="alice@example.com", token="super-secret")

    captured = capsys.readouterr()
    assert "a***@example.com" in captured.out
    assert "alice@example.com" not in captured.out
    assert "[REDACTED]" in captured.out
    assert "super-secret" not in captured.out
