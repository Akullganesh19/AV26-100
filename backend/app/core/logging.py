import logging
import sys
import structlog
import re

SENSITIVE_KEYS = {"email", "password", "password_hash", "clerk_id", "token", "access_token"}

def redact_pii_processor(logger, method_name, event_dict):
    """
    Structlog processor that redacts keys matching sensitive patterns
    and masks email addresses using regex to prevent active exposure.
    """
    for key in list(event_dict.keys()):
        # Structural redaction for exact sensitive keys
        if key.lower() in SENSITIVE_KEYS:
            event_dict[key] = "[REDACTED]"
            continue

        # Redact emails in string values (masking logic)
        val = event_dict[key]
        if isinstance(val, str):
            # Email regex to mask
            event_dict[key] = re.sub(r'([a-zA-Z0-9_.+-])[^@]*(@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', r'\1***\2', val)

    return event_dict

def setup_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            redact_pii_processor,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
