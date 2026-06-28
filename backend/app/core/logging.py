import logging
import sys
import structlog
import re

PII_KEYS = {"email", "password", "password_hash", "clerk_id", "ssn", "card_number", "dob", "date_of_birth"}
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

def redact_email_match(match) -> str:
    email = match.group(0)
    parts = email.split("@")
    if len(parts) == 2 and len(parts[0]) > 0:
        return f"{parts[0][0]}***@{parts[1]}"
    return "***@***.***"

def redact_string(text: str) -> str:
    if not isinstance(text, str):
        return text
    return EMAIL_REGEX.sub(redact_email_match, text)

def redact_pii_processor(logger, log_method, event_dict):
    """
    Redacts sensitive PII from log events and kwargs.
    """
    for key, value in list(event_dict.items()):
        if str(key).lower() in PII_KEYS:
            event_dict[key] = "[REDACTED]"
        elif isinstance(value, str):
            event_dict[key] = redact_string(value)

    return event_dict

def setup_logging():
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        redact_pii_processor,
    ]

    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
