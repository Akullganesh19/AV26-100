import logging
import sys
import structlog

SENSITIVE_KEYS = {"password", "password_hash", "clerk_id", "ssn", "card_number", "name", "vocal_metrics"}
EMAIL_KEYS = {"email"}

def mask_email(email: str) -> str:
    if not isinstance(email, str) or "@" not in email:
        return "[REDACTED]"
    user, domain = email.split("@", 1)
    if len(user) > 1:
        user = user[0] + "***"
    else:
        user = "***"
    return f"{user}@{domain}"

def redact_pii(obj, seen=None):
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return "<cyclic>"

    if isinstance(obj, dict):
        seen.add(obj_id)
        new_dict = {}
        for k, v in obj.items():
            if isinstance(k, str):
                k_lower = k.lower()
                if any(sec in k_lower for sec in SENSITIVE_KEYS):
                    new_dict[k] = "[REDACTED]"
                    continue
                elif any(em in k_lower for em in EMAIL_KEYS):
                    new_dict[k] = mask_email(v)
                    continue
            new_dict[k] = redact_pii(v, seen)
        seen.remove(obj_id)
        return new_dict
    elif isinstance(obj, list):
        seen.add(obj_id)
        new_list = [redact_pii(item, seen) for item in obj]
        seen.remove(obj_id)
        return new_list
    elif isinstance(obj, tuple):
        seen.add(obj_id)
        new_tuple = tuple(redact_pii(item, seen) for item in obj)
        seen.remove(obj_id)
        return new_tuple
    elif isinstance(obj, set):
        seen.add(obj_id)
        # Handle unhashable types if any sneak in by falling back to list
        try:
            new_set = {redact_pii(item, seen) for item in obj}
        except TypeError:
            new_set = [redact_pii(item, seen) for item in obj]
        seen.remove(obj_id)
        return new_set
    else:
        return obj

def redact_pii_processor(logger, method_name, event_dict):
    return redact_pii(event_dict)

def setup_logging():
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
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
            structlog.processors.JSONRenderer()
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
