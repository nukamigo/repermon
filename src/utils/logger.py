import sys
import logging
from typing import List, Optional


def setup_logger(
    name: str,
    level: Optional[int] = None,
    handlers: Optional[List[logging.Handler]] = None,
) -> logging.Logger:
    """
    Creates and configures a logger with the a name.
    Args:
        name: Logger name
        level: logging level
        handlers: List of logging.Handler instances to attach. Defaults to a StreamHandler.
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(level or logging.INFO)

    if handlers is None:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s]: %(message)s"
        )
        handler.setFormatter(formatter)
        handlers = [handler]

    for handler in handlers:
        logger.addHandler(handler)

    return logger
