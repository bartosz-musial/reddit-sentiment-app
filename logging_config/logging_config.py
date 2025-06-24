from .colour_logging import CustomFormatted
import logging

def get_config():
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