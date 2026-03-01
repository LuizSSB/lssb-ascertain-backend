from typing import Any

import pytest

from app.data.sqldatabase import SQLDatabase
from app.tooling.logging import AppLogger


@pytest.fixture
def logger() -> AppLogger:

    class DummyLogger(AppLogger):
        def info(self, event: str, **kwargs: Any):
            pass

        def warning(self, event: str, **kwargs: Any):
            pass

        def error(self, event: str, **kwargs: Any):
            pass

        def debug(self, event: str, **kwargs: Any):
            pass

        @classmethod
        def clear_context(cls):
            pass

        @classmethod
        def add_to_context(cls, **kwargs: Any):
            pass

        @classmethod
        def remove_from_context(cls, *args: str):
            pass

    return DummyLogger()


@pytest.fixture
async def database(logger: AppLogger) -> SQLDatabase:
    database = SQLDatabase("sqlite+aiosqlite:///:memory:", logger)
    await database.create_database()
    return database
