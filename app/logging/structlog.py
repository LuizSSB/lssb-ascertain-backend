import logging
from typing import Any, ClassVar

import structlog

from app.logging import AppLogger
from app.models.app_settings import AppSettings


class StructlogAppLogger(AppLogger):
    _is_set_up: ClassVar[bool] = False

    @staticmethod
    def _set_up():
        if StructlogAppLogger._is_set_up:
            return

        match AppSettings.default().ENV:
            case "dev":
                processors = (
                    structlog.processors.TimeStamper(fmt="iso", utc=False),
                    structlog.dev.ConsoleRenderer(),
                )
                wrapper_class = structlog.make_filtering_bound_logger(logging.NOTSET)
            case "prod":
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

    def __init__(self, **kwargs: Any):
        StructlogAppLogger._set_up()
        self._logger = structlog.get_logger(**kwargs)

    def info(self, event: str, **kwargs: Any):
        self._logger.info(event, **kwargs)

    def warning(self, event: str, **kwargs: Any):
        self._logger.warning(event, **kwargs)

    def error(self, event: str, **kwargs: Any):
        self._logger.error(event, **kwargs)

    def debug(self, event: str, **kwargs: Any):
        self._logger.debug(event, **kwargs)
