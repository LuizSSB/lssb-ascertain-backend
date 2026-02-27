from contextlib import asynccontextmanager

from models.app_settings import AppSettings
from models.sql import BaseSQLModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class SQLDatabase:
    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(db_url, echo=AppSettings.default().env == "dev")
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(BaseSQLModel.metadata.create_all)

    @asynccontextmanager
    async def session(self):
        session = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
