"""
colour_logging.py

This module defines a custom logging formatter that applies color coding
to log messages based on their severity level for better console readability.
"""

import logging

FMT = "{asctime} | {levelname} | {message}"
FORMATS = {
    logging.INFO: f"\33[32m{FMT}\33[0m",
    logging.WARNING: f"\33[33m{FMT}\33[0m",
    logging.ERROR: f"\33[29m{FMT}\33[0m",
}

class CustomFormatted(logging.Formatter):
    """
    Custom logging formatter that colors messages by log level.

    Methods:
    - format: Applies color formatting to log messages.
    """

    def format(self, record):
        # Format log record with color according to its level
        log_fmt = FORMATS.get(record.levelno, FMT)
        formatter = logging.Formatter(log_fmt, style="{", datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)
