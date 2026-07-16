import logging
import sys
import structlog

def mask_email(email_str):
    if not isinstance(email_str, str) or "@" not in email_str:
        return "[REDACTED]"
    parts = email_str.split("@", 1)
    if len(parts[0]) > 0:
        return f"{parts[0][0]}***@{parts[1]}"
    return "***@" + parts[1]

def redact_pii_processor(logger, log_method, event_dict):
    def _redact(data, seen=None):
        if seen is None:
            seen = set()

        obj_id = id(data)
        if obj_id in seen:
            return "<cyclic-reference>"

        if isinstance(data, dict):
            seen.add(obj_id)
            new_dict = {}
            for k, v in data.items():
                is_sensitive_key = isinstance(k, str) and any(
                    part in k.lower() for part in ("email", "emails")
                )

                if is_sensitive_key:
                    if isinstance(v, str):
                        new_dict[k] = mask_email(v)
                    elif isinstance(v, (list, tuple)):
                        seen.add(id(v))
                        new_dict[k] = type(v)(mask_email(item) if isinstance(item, str) else _redact(item, seen) for item in v)
                        seen.remove(id(v))
                    else:
                        new_dict[k] = _redact(v, seen)
                else:
                    new_dict[k] = _redact(v, seen)
            seen.remove(obj_id)
            return new_dict
        elif isinstance(data, (list, tuple)):
            seen.add(obj_id)
            new_list = type(data)(_redact(item, seen) for item in data)
            seen.remove(obj_id)
            return new_list
        else:
            return data

    return _redact(event_dict)

def setup_logging():
    shared_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        structlog.contextvars.merge_contextvars,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        redact_pii_processor,
    ]

    structlog.configure(
        processors=shared_processors + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
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
