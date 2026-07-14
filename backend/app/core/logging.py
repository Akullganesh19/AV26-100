import logging
import sys
import structlog

def mask_email(email: str) -> str:
    if not isinstance(email, str) or '@' not in email:
        return str(email)
    parts = email.split('@')
    if len(parts) != 2:
        return email
    user, domain = parts
    if len(user) > 1:
        masked_user = user[0] + "***"
    else:
        masked_user = "***"
    return f"{masked_user}@{domain}"

def redact_data(data, seen=None):
    if seen is None:
        seen = set()

    obj_id = id(data)
    if obj_id in seen:
        return "<cyclic-reference>"

    if isinstance(data, dict):
        seen.add(obj_id)
        new_dict = {}
        for k, v in data.items():
            if isinstance(k, str) and k.lower() in ("email", "emails", "email_address"):
                if isinstance(v, str):
                    new_dict[k] = mask_email(v)
                elif isinstance(v, (list, tuple)):
                    new_dict[k] = [mask_email(item) if isinstance(item, str) else redact_data(item, seen) for item in v]
                else:
                    new_dict[k] = redact_data(v, seen)
            else:
                new_dict[k] = redact_data(v, seen)
        seen.remove(obj_id)
        return new_dict
    elif isinstance(data, (list, tuple)):
        seen.add(obj_id)
        new_list = [redact_data(item, seen) for item in data]
        seen.remove(obj_id)
        return new_list if isinstance(data, list) else tuple(new_list)
    else:
        return data

def redact_pii_processor(logger, method_name, event_dict):
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
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
