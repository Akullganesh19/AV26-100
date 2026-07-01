import logging
import sys
import structlog
import re

SENSITIVE_KEYS = {"email", "password", "password_hash", "ssn", "clerk_id", "address", "dob", "date_of_birth", "card_number", "phone"}
EMAIL_REGEX = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")

def redact_pii_processor(logger, log_method, event_dict):
    def redact_val(k, v):
        if isinstance(k, str) and k.lower() in SENSITIVE_KEYS:
            return "[REDACTED]"
        if isinstance(v, dict):
            return {nk: redact_val(nk, nv) for nk, nv in v.items()}
        if isinstance(v, list):
            return [redact_val(k, item) for item in v]
        if isinstance(v, str):
            v = EMAIL_REGEX.sub(r"[REDACTED_EMAIL]", v)
        return v

    return {k: redact_val(k, v) for k, v in event_dict.items()}

def setup_logging():
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.ExtraAdder(),
        redact_pii_processor,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    structlog.configure(
        processors=shared_processors + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
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
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
