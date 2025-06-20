import sys
from functools import cache

from loguru import logger as loguru_logger
from loguru._logger import Logger

__all__ = ["get_logger", "logger"]


DEFAULT_LOGGER_NAME = "KSF Tech Task"
DEFAULT_MESSAGE_FORMAT = "<level>{level}</level>:\t  {message}"


def _setup_default_logger(context_logger: Logger) -> None:
    context_logger.add(
        sink=sys.stdout, colorize=True, format=DEFAULT_MESSAGE_FORMAT, backtrace=True
    )


def _setup_logger(name: str) -> Logger:
    """
    Return configured logger.
    """
    loguru_logger.remove()
    context_logger = loguru_logger.bind(name=name)
    _setup_default_logger(context_logger)
    context_logger.level("INFO", color="<green>")
    context_logger.level("WARNING", color="<yellow>")
    context_logger.level("ERROR", color="<red>")
    return context_logger


@cache
def get_logger(name: str = DEFAULT_LOGGER_NAME) -> Logger:
    """
    Initialize logger for a project.
    """
    return _setup_logger(name)


logger = get_logger()
