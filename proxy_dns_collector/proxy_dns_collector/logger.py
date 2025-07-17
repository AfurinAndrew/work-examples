import os
import logging

try:
    CURRENT_USER = os.getlogin() if hasattr(os, "getlogin") else "Unknown"
except OSError:
    CURRENT_USER = os.environ.get(
        "USER") or os.environ.get("LOGNAME") or "Unknown"


def setup_logger(name: str, log_file: str, level: str = "INFO") -> logging.LoggerAdapter:
    # Map string log level to logging level constant
    logger_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    level = logger_level_map.get(level.upper())

    logger = logging.getLogger(name)
    logger.setLevel(level)

    file_handler = logging.FileHandler(log_file, mode="a")
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(fmt="%(asctime)s %(name)s[%(process)d]: %(levelname)s [%(user)s] %(message)s",
                                        datefmt="%b %d %H:%M:%S")
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)

    logger = logging.LoggerAdapter(logger, {"user": CURRENT_USER})

    return logger
