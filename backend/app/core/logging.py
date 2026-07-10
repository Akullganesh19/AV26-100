import logging
import sys
import structlog
import copy

def mask_email(email: str) -> str:
    if not isinstance(email, str) or "@" not in email:
        return email
    parts = email.split("@", 1)
    if not parts[0]:
        return email
    return f"{parts[0][0]}***@{parts[1]}"

def redact_pii_processor(logger, method_name, event_dict):
    def _redact(data, seen_ids):
        if id(data) in seen_ids:
            return "<cyclic>"

        seen_ids.add(id(data))

        if isinstance(data, dict):
            new_data = {}
            for k, v in data.items():
                if isinstance(k, str) and any(x in k.lower() for x in ["email", "emails", "to_email"]):
                    if isinstance(v, str):
                        new_data[k] = mask_email(v)
                    elif isinstance(v, (list, tuple)):
                        new_data[k] = [mask_email(item) if isinstance(item, str) else _redact(item, seen_ids.copy()) for item in v]
                    else:
                        new_data[k] = _redact(v, seen_ids.copy())
                else:
                    new_data[k] = _redact(v, seen_ids.copy())
            return new_data
        elif isinstance(data, (list, tuple)):
            return [_redact(item, seen_ids.copy()) for item in data]
        else:
            return data

    return _redact(event_dict, set())

def setup_logging():
    shared_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        structlog.contextvars.merge_contextvars,
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
            structlog.processors.JSONRenderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(handler)
    from app.core.config import settings
    root_logger.setLevel(settings.LOG_LEVEL)
