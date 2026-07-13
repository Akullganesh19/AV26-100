import logging
import sys
import structlog

def redact_pii_processor(logger, log_method, event_dict):
    """
    Redacts PII (like email) from the structlog event_dict safely.
    It returns a new dict to avoid corrupting active memory.
    """
    PII_KEYS = {"email", "phone", "password", "ssn", "address", "dob", "card_number"}

    def _mask_email(email_str):
        if not isinstance(email_str, str):
            return email_str
        parts = email_str.split("@")
        if len(parts) == 2:
            name, domain = parts
            masked_name = name[0] + "***" if len(name) > 0 else "***"
            return f"{masked_name}@{domain}"
        return "***"

    def _redact(data, seen=None):
        if seen is None:
            seen = set()

        data_id = id(data)
        if data_id in seen:
            return "<cyclic-reference>"

        if isinstance(data, dict):
            seen.add(data_id)
            new_dict = {}
            for k, v in data.items():
                is_pii = isinstance(k, str) and k.lower() in PII_KEYS
                if is_pii:
                    if isinstance(k, str) and k.lower() == "email":
                        new_dict[k] = _mask_email(v)
                    else:
                        new_dict[k] = "[REDACTED]"
                else:
                    new_dict[k] = _redact(v, seen)
            seen.remove(data_id)
            return new_dict
        elif isinstance(data, (list, tuple)):
            seen.add(data_id)
            new_list = [_redact(item, seen) for item in data]
            seen.remove(data_id)
            return type(data)(new_list)
        else:
            return data

    return _redact(event_dict)


def setup_logging():
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
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
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processor=structlog.processors.JSONRenderer(),
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
