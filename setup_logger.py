import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_worker_logger(service_name: str, log_file: str) -> logging.Logger:
    logger = logging.getLogger(service_name)
    
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] (%(filename)s:%(lineno)d) | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
        )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger