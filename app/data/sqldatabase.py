import time
from contextlib import asynccontextmanager
from typing import Any, ClassVar

from sqlalchemy import event
from sqlalchemy.engine import Connection, Engine, ExecutionContext, make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.models.app_settings import AppSettings
from app.tooling.logging import AppLogger


def _mask_connection_string(connection_string: str) -> str:
    try:
        url = make_url(connection_string)
        masked_url = url.set(username="xxx", password="xxx")
        return masked_url.render_as_string(hide_password=False)
    except Exception:
        return "xxx"


@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(
    conn: Connection, cursor: Any, statement: str, parameters: Any, context: ExecutionContext, execmany: bool
) -> None:
    # Attach start time to the context object to ensure thread/task safety
    setattr(context, "_query_start_time", time.time())


_THRESHOLD_SLOW_QUERY_MS = 500


class SQLDatabase:
    _instance: ClassVar["SQLDatabase | None"] = None

    def __init__(self, db_url: str, logger: AppLogger):
        if SQLDatabase._instance:
            raise Exception("Trying to reinstantiate singleton SQLDatabase")

        self.logger = logger
        self.logger.info("Initializing SQLDatabase", db_url=_mask_connection_string(db_url))
        self._engine = create_async_engine(db_url, echo=AppSettings.default().ENV == "dev")
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )
        SQLDatabase._instance = self

    @staticmethod
    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(
        conn: Connection, cursor: Any, statement: str, parameters: Any, context: ExecutionContext, execmany: bool
    ) -> None:
        if not SQLDatabase._instance:
            raise Exception("Query being executed without SQLDatabase")

        start_time = getattr(context, "_query_start_time", 0.0)
        if start_time == 0.0:
            return

        duration_ms = (time.time() - start_time) * 1000
        query_preview: str = statement.splitlines()[0]

        if duration_ms > _THRESHOLD_SLOW_QUERY_MS:
            SQLDatabase._instance.logger.warning(
                "slow_query_detected", duration_ms=round(duration_ms, 2), query=query_preview
            )
        else:
            SQLDatabase._instance.logger.debug("query_executed", duration_ms=round(duration_ms, 2), query=query_preview)

    async def create_database(self):
        self.logger.info("Creating database schema", tables=list(SQLModel.metadata.tables.keys()))
        async with self._engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        self.logger.info("Database schema created")

    @asynccontextmanager
    async def session(self):
        self.logger.debug("Opening new database session")
        session = self._session_factory()
        try:
            yield session
        except Exception as e:
            self.logger.error("Session rollback due to exception", error=str(e))
            await session.rollback()
            raise
        finally:
            await session.close()
            self.logger.debug("Database session closed")
