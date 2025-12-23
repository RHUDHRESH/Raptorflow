import logging
import sys
from datetime import datetime

from pythonjsonlogger import jsonlogger


class RaptorFlowJSONFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(RaptorFlowJSONFormatter, self).add_fields(
            log_record, record, message_dict
        )
        if not log_record.get("timestamp"):
            now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now

        # GCP Cloud Logging expects 'severity' for automatic log level detection
        if log_record.get("level"):
            level = log_record["level"].upper()
            log_record["level"] = level
            log_record["severity"] = level
        else:
            level = record.levelname.upper()
            log_record["level"] = level
            log_record["severity"] = level


def setup_logger():
    logger = logging.getLogger("raptorflow")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = RaptorFlowJSONFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = logging.getLogger("raptorflow")
if not logger.handlers:
    logger = setup_logger()


def log_ml_event(event_type: str, payload: dict):
    """Specialized logger for MLOps audit trails."""
    logger.info(
        f"ML_EVENT: {event_type}",
        extra={"event_type": event_type, "ml_payload": payload},
    )
