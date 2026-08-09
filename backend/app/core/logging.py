import logging
import sys
import structlog
from typing import Any

def _redact_value(key: str, value: Any) -> Any:
    if not isinstance(key, str):
        return value

    key_lower = key.lower()

    if "email" in key_lower:
        if isinstance(value, str):
            parts = value.split("@")
            if len(parts) == 2 and parts[0]:
                return f"{parts[0][0]}***@{parts[1]}"
            return "***"
        return "***"

    sensitive_keys = ["phone", "ssn", "address", "dob", "date_of_birth", "password", "card_number"]
    if any(s_key in key_lower for s_key in sensitive_keys):
        return "***"

    return value

def redact_pii_processor(logger, log_method, event_dict):
    def _traverse(data: Any, seen: set) -> Any:
        # For immutable types like int, str, float, bool, None, id() check isn't necessary
        # but let's check for dict/list/tuple to track cyclic references
        if isinstance(data, (dict, list, tuple)):
            obj_id = id(data)
            if obj_id in seen:
                return "<cyclic-reference>"

            new_seen = seen | {obj_id}

            if isinstance(data, dict):
                new_dict = {}
                for k, v in data.items():
                    if isinstance(k, str):
                        new_dict[k] = _traverse(_redact_value(k, v), new_seen)
                    else:
                        new_dict[k] = _traverse(v, new_seen)
                return new_dict

            elif isinstance(data, list):
                return [_traverse(item, new_seen) for item in data]

            elif isinstance(data, tuple):
                return tuple(_traverse(item, new_seen) for item in data)

        return data

    return _traverse(event_dict, set())

def setup_logging():
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        redact_pii_processor,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
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
