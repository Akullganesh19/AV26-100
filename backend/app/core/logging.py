import logging
import sys
import structlog
import re

SENSITIVE_KEYS = {"email", "password", "ssn", "clerk_id"}

def mask_string(s: str) -> str:
    # simple email mask, preserving context
    return re.sub(r'([a-zA-Z0-9_.+-])[a-zA-Z0-9_.+-]*@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', r'\1***@\2', s)

def redact_value(key: str, value: any) -> any:
    if isinstance(key, str) and key.lower() in SENSITIVE_KEYS:
        if key.lower() == 'email' and isinstance(value, str):
            return mask_string(value)
        return "[REDACTED]"

    if isinstance(value, dict):
        redact_dict(value)
        return value
    elif isinstance(value, list):
        for i, item in enumerate(value):
            value[i] = redact_value(key, item)
        return value
    elif isinstance(value, str):
        return mask_string(value)

    return value

def redact_dict(d: dict):
    for k, v in d.items():
        d[k] = redact_value(k, v)

def redact_pii_processor(logger, log_method, event_dict):
    redact_dict(event_dict)
    return event_dict

def setup_logging():
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
        redact_pii_processor,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
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
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
