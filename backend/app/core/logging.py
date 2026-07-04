import logging
import sys
import structlog
import re

SENSITIVE_KEYS = {"email", "password", "ssn", "clerk_id", "password_hash"}
EMAIL_REGEX = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")

def mask_email(match):
    email = match.group(0)
    parts = email.split('@')
    if len(parts) != 2:
        return "***@***.***"

    user_part, domain_part = parts
    if len(user_part) > 1:
        masked_user = user_part[0] + "***"
    else:
        masked_user = "***"

    return f"{masked_user}@{domain_part}"

def _redact(obj, seen=None):
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return "<CyclicReference>"

    seen.add(obj_id)

    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if str(k).lower() in SENSITIVE_KEYS:
                new_dict[k] = "***REDACTED***"
            else:
                new_dict[k] = _redact(v, seen)
        seen.remove(obj_id)
        return new_dict
    elif isinstance(obj, list):
        new_list = [_redact(item, seen) for item in obj]
        seen.remove(obj_id)
        return new_list
    elif isinstance(obj, str):
        seen.remove(obj_id)
        return EMAIL_REGEX.sub(mask_email, obj)
    else:
        seen.remove(obj_id)
        return obj

def redact_pii_processor(logger, log_method, event_dict):
    # Instead of a full deep copy, rebuild the dictionary handling
    # cyclic references and ignoring unpickable elements natively
    # via the _redact function's traversal.
    redacted_event_dict = _redact(event_dict)

    # Mask strings in event
    event = redacted_event_dict.get("event")
    if isinstance(event, str):
        redacted_event_dict["event"] = EMAIL_REGEX.sub(mask_email, event)

    return redacted_event_dict

def setup_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.stdlib.ExtraAdder(),
            redact_pii_processor,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.ExtraAdder(),
            redact_pii_processor,
        ],
        processors=[
            structlog.processors.JSONRenderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    # Remove existing handlers to avoid duplicates if setup_logging is called multiple times
    root_logger.handlers.clear()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)
