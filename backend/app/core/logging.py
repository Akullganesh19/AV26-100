import logging
import sys
import structlog
from copy import deepcopy

PII_KEYS = {"email", "password", "password_hash", "ssn", "phone", "card_number", "dob", "date_of_birth", "address", "name"}

def redact_data(obj, seen=None):
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return "<cyclic_reference>"

    if isinstance(obj, dict):
        seen.add(obj_id)
        new_dict = {}
        for k, v in obj.items():
            if isinstance(k, str) and k.lower() in PII_KEYS:
                # Mask email like j***@gmail.com if possible
                if k.lower() == "email" and isinstance(v, str) and "@" in v:
                    parts = v.split("@", 1)
                    if len(parts[0]) > 0:
                        masked = parts[0][0] + "***" + "@" + parts[1]
                    else:
                        masked = "***" + "@" + parts[1]
                    new_dict[k] = masked
                else:
                    new_dict[k] = "[REDACTED]"
            else:
                new_dict[k] = redact_data(v, seen)
        seen.remove(obj_id)
        return new_dict
    elif isinstance(obj, list):
        seen.add(obj_id)
        new_list = [redact_data(item, seen) for item in obj]
        seen.remove(obj_id)
        return new_list
    elif hasattr(obj, "__dict__"):
        return obj
    else:
        return obj

def redact_pii_processor(logger, log_method, event_dict):
    return redact_data(event_dict)

def setup_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.ExtraAdder(),
            redact_pii_processor,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
        foreign_pre_chain=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.ExtraAdder(),
            redact_pii_processor,
            structlog.processors.TimeStamper(fmt="iso"),
        ]
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
