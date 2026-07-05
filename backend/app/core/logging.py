import logging
import sys
import structlog
import re

SENSITIVE_KEYS = {"email", "password", "password_hash", "ssn", "clerk_id", "token", "access_token"}
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

def _redact_value(key: str, value: any, seen_ids: set) -> any:
    if isinstance(value, str):
        if isinstance(key, str) and key.lower() in SENSITIVE_KEYS:
            return "***REDACTED***"
        if EMAIL_REGEX.search(value):
            return EMAIL_REGEX.sub(lambda m: m.group(0)[0] + "***" + m.group(0)[m.group(0).find("@"):], value)
        return value

    if isinstance(value, dict):
        if id(value) in seen_ids:
            return "<cyclic>"
        seen_ids.add(id(value))
        new_dict = {}
        for k, v in value.items():
            new_dict[k] = _redact_value(k, v, seen_ids)
        seen_ids.remove(id(value))
        return new_dict

    if isinstance(value, (list, tuple)):
        if id(value) in seen_ids:
            return "<cyclic>"
        seen_ids.add(id(value))
        new_list = [_redact_value(key, item, seen_ids) for item in value]
        seen_ids.remove(id(value))
        return tuple(new_list) if isinstance(value, tuple) else new_list

    return value

def redact_pii_processor(logger, log_method, event_dict):
    seen_ids = set()
    new_event_dict = {}
    for key, value in event_dict.items():
        new_event_dict[key] = _redact_value(key, value, seen_ids)
    return new_event_dict

def setup_logging():
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        redact_pii_processor,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.ExtraAdder(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            redact_pii_processor,
        ]
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
