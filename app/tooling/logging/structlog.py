import logging
from typing import Any
from uuid import uuid4

import structlog

from app.models.app_settings import AppSettings
from app.tooling.logging import AppLogger
from app.utils.functions import run_once


@run_once
def _set_up():
    if AppSettings.EnvTraits.CAN_LOG_DEBUG in AppSettings.default().env_traits:
        processors = (
            structlog.processors.TimeStamper(fmt="iso", utc=False),
            structlog.dev.ConsoleRenderer(),
        )
        wrapper_class = structlog.make_filtering_bound_logger(logging.NOTSET)
    else:
        processors = (
            structlog.processors.TimeStamper(fmt="iso", utc=False),
            structlog.processors.JSONRenderer(),
        )
        wrapper_class = structlog.make_filtering_bound_logger(20)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            *processors,
        ],
        wrapper_class=wrapper_class,
        cache_logger_on_first_use=True,
    )


class StructlogAppLogger(AppLogger):
    def __init__(self, name: str, **kwargs: Any):
        _set_up()
        args = {"_id": str(uuid4()), "_name": name} | kwargs
        self._logger = structlog.get_logger(**args)

    def info(self, event: str, **kwargs: Any):
        self._logger.info(event, **kwargs)

    def warning(self, event: str, **kwargs: Any):
        self._logger.warning(event, **kwargs)

    def error(self, event: str, **kwargs: Any):
        self._logger.error(event, **kwargs)

    def debug(self, event: str, **kwargs: Any):
        self._logger.debug(event, **kwargs)

    @classmethod
    def clear_context(cls):
        structlog.contextvars.clear_contextvars()

    @classmethod
    def add_to_context(cls, **kwargs: Any):
        structlog.contextvars.bind_contextvars(**kwargs)

    @classmethod
    def remove_from_context(cls, *args: str):
        structlog.contextvars.unbind_contextvars(*args)
