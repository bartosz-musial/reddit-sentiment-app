import logging

FMT = "{asctime} | {levelname} | {message}"
FORMATS = {
    logging.INFO: f"\33[32m{FMT}\33[0m",
    logging.WARNING: f"\33[33m{FMT}\33[0m",
    logging.ERROR: f"\33[29m{FMT}\33[0m",
}

class CustomFormatted(logging.Formatter):
    def format(self, record):
        log_fmt = FORMATS.get(record.levelno, FMT)
        formatter = logging.Formatter(log_fmt, style="{", datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)
