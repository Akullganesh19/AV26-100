import logging
import sys
import structlog

SENSITIVE_KEYS = {"email", "password", "password_hash", "clerk_id", "phone", "ssn", "address", "dob", "date_of_birth", "card_number", "token", "access_token"}

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
            if isinstance(k, str) and k.lower() in SENSITIVE_KEYS:
                # Mask sensitive fields. For email, we show context like j***@gmail.com
                if k.lower() == "email" and isinstance(v, str) and "@" in v:
                    username, domain = v.split("@", 1)
                    if username:
                        new_dict[k] = f"{username[0]}***@{domain}"
                    else:
                        new_dict[k] = f"***@{domain}"
                else:
                    new_dict[k] = "***"
            else:
                new_dict[k] = redact_data(v, seen)
        seen.remove(obj_id)
        return new_dict
    elif isinstance(data, (list, tuple)):
        seen.add(obj_id)
        is_tuple = isinstance(data, tuple)
        new_list = [redact_data(item, seen) for item in data]
        seen.remove(obj_id)
        return tuple(new_list) if is_tuple else new_list
    else:
        return data

def redact_pii_processor(logger, method_name, event_dict):
    return redact_data(event_dict)

def setup_logging():
    processor_chain = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.stdlib.ExtraAdder(),
        redact_pii_processor,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(
        processors=processor_chain,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.ExtraAdder(),
            redact_pii_processor,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    # The log level should be controlled by root logger,
    # but we avoid hardcoding it so it defaults to INFO and respects config.py's changes.
