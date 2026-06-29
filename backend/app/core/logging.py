import logging
import sys
import structlog
import re

SENSITIVE_KEYS = {"email", "password", "ssn", "clerk_id"}
EMAIL_REGEX = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")

def mask_email(match):
    email = match.group(1)
    parts = email.split('@')
    if len(parts) == 2:
        name, domain = parts
        masked_name = name[0] + "***" if len(name) > 0 else "***"
        return f"{masked_name}@{domain}"
    return "***@***"

def _recursive_redact(data):
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if key in SENSITIVE_KEYS:
                data[key] = "[REDACTED]"
            else:
                data[key] = _recursive_redact(value)
        return data
    elif isinstance(data, list):
        return [_recursive_redact(item) for item in data]
    elif isinstance(data, str):
        return EMAIL_REGEX.sub(mask_email, data)
    else:
        return data

def redact_pii_processor(logger, log_method, event_dict):
    return _recursive_redact(event_dict)

def setup_logging():
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
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
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
