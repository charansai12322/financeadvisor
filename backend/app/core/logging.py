"""
Structured logging configuration with secret redaction.
"""
import logging
import re
import sys
from typing import Optional

# Secret redaction patterns
REDACTION_PATTERNS = [
    (re.compile(r"AIza[0-9A-Za-z-_]{35}"), "[REDACTED_GOOGLE_API_KEY]"),
    (re.compile(r"(?i)(api[_-]?key[\"\'\s:=]+)([a-zA-Z0-9_\-]{16,})"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(bearer[\s:]+)([a-zA-Z0-9_\-\.]{16,})"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(authorization[\"\'\s:=]+)([^\s,;]+)"), r"\1[REDACTED]"),
]


class SensitiveFilter(logging.Filter):
    """Filter that redacts credentials and sensitive tokens from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            msg = record.msg
            for pattern, replacement in REDACTION_PATTERNS:
                msg = pattern.sub(replacement, msg)
            record.msg = msg
        return True


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configures application logger with formatter and sensitive data filter."""
    logger = logging.getLogger("finance_advisor")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.addFilter(SensitiveFilter())
        logger.addHandler(handler)

    return logger


logger = setup_logging()
