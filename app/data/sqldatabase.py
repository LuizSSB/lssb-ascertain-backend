from contextlib import asynccontextmanager

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.logging import AppLogger
from app.models.app_settings import AppSettings


def _mask_connection_string(connection_string: str) -> str:
    try:
        url = make_url(connection_string)
        masked_url = url.set(username="xxx", password="xxx")
        return masked_url.render_as_string(hide_password=False)
    except Exception:
        return "xxx"


class SQLDatabase:
    def __init__(self, db_url: str, logger: AppLogger):
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
