import logging
import sys
import structlog

def partially_mask_email(email: str) -> str:
    try:
        if "@" in email:
            local, domain = email.split("@", 1)
            if len(local) > 1:
                masked_local = local[0] + "***"
            else:
                masked_local = "***"
            return f"{masked_local}@{domain}"
    except Exception:
        pass
    return "***@***"

def redact_value(key: str, value: any) -> any:
    if not isinstance(key, str):
        return value

    key_lower = key.lower()
    if any(k in key_lower for k in ["email"]):
        if isinstance(value, str):
            return partially_mask_email(value)
        return "***@***"
    elif any(k in key_lower for k in ["password", "secret", "token", "ssn", "card", "clerk_id", "phone", "address"]):
        return "[REDACTED]"
    return value

def _redact_dict(data: dict, seen_ids: set) -> dict:
    if id(data) in seen_ids:
        return "<cyclic>"
    seen_ids.add(id(data))

    new_dict = {}
    for k, v in data.items():
        if isinstance(v, dict):
            new_dict[k] = _redact_dict(v, seen_ids)
        elif isinstance(v, list):
            new_dict[k] = _redact_list(v, seen_ids)
        else:
            new_dict[k] = redact_value(k, v)

    seen_ids.remove(id(data))
    return new_dict

def _redact_list(data: list, seen_ids: set) -> list:
    if id(data) in seen_ids:
        return ["<cyclic>"]
    seen_ids.add(id(data))

    new_list = []
    for item in data:
        if isinstance(item, dict):
            new_list.append(_redact_dict(item, seen_ids))
        elif isinstance(item, list):
            new_list.append(_redact_list(item, seen_ids))
        else:
            new_list.append(item)

    seen_ids.remove(id(data))
    return new_list

def redact_pii_processor(logger, method_name, event_dict):
    seen_ids = set()
    return _redact_dict(event_dict, seen_ids)

shared_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.dev.set_exc_info,
    structlog.processors.TimeStamper(fmt="iso"),
    redact_pii_processor,
]

def setup_logging():
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
