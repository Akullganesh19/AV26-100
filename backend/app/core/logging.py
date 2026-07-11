import logging
import sys
import structlog
import copy

def redact_pii_processor(logger, log_method, event_dict):
    """
    Recursively redact sensitive data (PII) from log records to prevent leaks.
    Safely handles cyclic references.
    """
    def redact(data, seen_ids=None):
        if seen_ids is None:
            seen_ids = set()

        if id(data) in seen_ids:
            return "<cyclic-reference>"

        # Don't track primitive types
        if not isinstance(data, (dict, list, tuple)):
            return data

        seen_ids.add(id(data))

        if isinstance(data, dict):
            new_data = {}
            for key, value in data.items():
                if isinstance(key, str) and key.lower() in ("email", "user_email", "email_address"):
                    if isinstance(value, str):
                        # Mask email partially: j***@domain.com
                        parts = value.split('@')
                        if len(parts) == 2 and len(parts[0]) > 0:
                            masked_name = parts[0][0] + "***"
                            new_data[key] = f"{masked_name}@{parts[1]}"
                        else:
                            new_data[key] = "[REDACTED]"
                    else:
                        new_data[key] = "[REDACTED]"
                elif isinstance(key, str) and key.lower() in ("password", "password_hash", "token", "ssn", "secret", "clerk_id", "secret_key"):
                    new_data[key] = "[REDACTED]"
                else:
                    new_data[key] = redact(value, seen_ids)
            seen_ids.remove(id(data))
            return new_data
        elif isinstance(data, list):
            new_list = [redact(item, seen_ids) for item in data]
            seen_ids.remove(id(data))
            return new_list
        elif isinstance(data, tuple):
            new_tuple = tuple(redact(item, seen_ids) for item in data)
            seen_ids.remove(id(data))
            return new_tuple

        seen_ids.remove(id(data))
        return data

    return redact(event_dict)

def setup_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ExtraAdder(),
            redact_pii_processor,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.ExtraAdder(),
            redact_pii_processor,
        ],
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    # Remove existing handlers
    root_logger.handlers = []
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
