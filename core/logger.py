"""Structured logging for the core engine."""

import logging
import sys

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


def setup_logger(name: str = "awe", level: str = "info") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(LEVELS.get(level, logging.INFO))

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(
        "[%(name)s] %(levelname)s: %(message)s"
    ))
    logger.addHandler(handler)
    return logger


log = setup_logger()
