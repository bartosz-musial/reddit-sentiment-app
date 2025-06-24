import logging

def get_config():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
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