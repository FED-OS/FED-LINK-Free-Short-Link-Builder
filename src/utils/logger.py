"""Logging helpers for FED-LINk.

One logger for the whole project, configured once from ``setup_logging``.
CLI runs log to the console; desktop builds log to ``logs/build.log`` as well
so the packaged app still leaves a paper trail.
"""

import logging
import os
import sys

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _build_handlers(console: bool, logfile: str | None) -> list[logging.Handler]:
    handlers: list[logging.Handler] = []
    if console:
        handlers.append(logging.StreamHandler(sys.stdout))
    if logfile:
        directory = os.path.dirname(os.path.abspath(logfile))
        os.makedirs(directory, exist_ok=True)
        handlers.append(logging.FileHandler(logfile, encoding="utf-8"))
    return handlers


def setup_logging(level: int = logging.INFO, console: bool = True,
                  logfile: str | None = None) -> logging.Logger:
    """Configure and return the shared ``fedlink`` logger.

    Safe to call more than once: previous handlers are removed first.
    """
    logger = logging.getLogger("fedlink")
    logger.setLevel(level)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
    for handler in _build_handlers(console, logfile):
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if not logger.handlers:  # never return a logger that cannot emit
        logger.addHandler(logging.NullHandler())
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a child logger (e.g. ``fedlink.generator``)."""
    if not name:
        return logging.getLogger("fedlink")
    if name.startswith("fedlink."):
        return logging.getLogger(name)
    return logging.getLogger("fedlink." + name)
