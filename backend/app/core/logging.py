import logging
import sys
import structlog

def partially_mask_email(email: str) -> str:
    if not isinstance(email, str) or "@" not in email:
        return "[REDACTED]"
    parts = email.split("@", 1)
    if len(parts) == 2:
        local, domain = parts
        if len(local) > 1:
            masked_local = local[0] + "***"
        else:
            masked_local = "***"
        return f"{masked_local}@{domain}"
    return "[REDACTED]"

def redact_data(data, seen_ids=None):
    if seen_ids is None:
        seen_ids = set()

    if id(data) in seen_ids:
        return "<cyclic-reference>"

    seen_ids.add(id(data))

    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            if isinstance(k, str) and k.lower() in ("email", "emails"):
                if isinstance(v, (list, tuple)):
                    new_dict[k] = type(v)(partially_mask_email(item) if isinstance(item, str) else redact_data(item, seen_ids.copy()) for item in v)
                elif isinstance(v, str):
                    new_dict[k] = partially_mask_email(v)
                else:
                    new_dict[k] = redact_data(v, seen_ids.copy())
            elif isinstance(k, str) and any(pii_key in k.lower() for pii_key in ("password", "ssn", "phone", "address", "card_number", "dob", "date_of_birth")):
                new_dict[k] = "[REDACTED]"
            else:
                new_dict[k] = redact_data(v, seen_ids.copy())
        return new_dict
    elif isinstance(data, list):
        return [redact_data(item, seen_ids.copy()) for item in data]
    elif isinstance(data, tuple):
        return tuple(redact_data(item, seen_ids.copy()) for item in data)
    else:
        return data

def redact_pii_processor(logger, log_method, event_dict):
    return redact_data(event_dict)

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
    root_logger.handlers = []
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
