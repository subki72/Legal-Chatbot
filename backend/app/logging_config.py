import json
import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter for enterprise observability.

    Formats log records into normalized JSON strings compatible with log ingestion
    pipelines such as Datadog, Grafana Loki, AWS CloudWatch, and ELK Stack.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format the specified record as a serialized JSON string.

        Args:
            record: The LogRecord instance to format.

        Returns:
            str: JSON-encoded log line.
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_entry.update(record.extra_data)

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(level: int = logging.INFO, use_json: bool = True) -> None:
    """Configure the root logger with standard stream handlers and formatters.

    Args:
        level: Logging threshold level (default: logging.INFO).
        use_json: If True, uses JSONFormatter; otherwise standard plaintext formatting.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clean existing handlers to prevent duplicate output
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    if use_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )

    root_logger.addHandler(console_handler)
