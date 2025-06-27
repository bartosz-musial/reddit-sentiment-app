"""
logger_config.py

This module configures the root logger with a custom stream handler
using the CustomFormatted formatter for colored log output.

It also sets log levels to ERROR for specified noisy libraries to reduce verbosity.
"""

from .colour_logging import CustomFormatted
import logging

def get_config():
    """
    Set up logging configuration with custom formatting and
    reduced log verbosity for selected libraries.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatted())
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
    )

    for lib in [
        "apscheduler.scheduler",
        "apscheduler.executors.default",
        "apscheduler.jobstores.default",
        "apscheduler.events",
        "apscheduler.triggers",
        "psycopg2",
        "openai",
        "praw",
    ]:
        logging.getLogger(lib).setLevel(logging.ERROR)

    logging.info("Logger configured")