from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import asc, desc, func, or_, select

from app.data.sqldatabase import AsyncSessionFactory
from app.data.user import UserRepository
from app.models.sql.user import SQLUser
from app.models.user import User, UserBaseData, UserUpdateData
from app.models.utils import SortFieldData
from app.tooling.logging import AppLogger


class SQLUserRepository(UserRepository):

    def __init__(self, session_factory: AsyncSessionFactory, logger: AppLogger) -> None:
        self.session_factory = session_factory
        self.logger = logger

    async def list_users(
        self,
        *,
        name: str | None = None,
        sort_by: SortFieldData[User.SortField] | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Iterable[User]:
        self.logger.debug("list_users called", name=name, sort_by=sort_by, skip=skip, limit=limit)

        async with self.session_factory() as session:
            query = select(SQLUser)
            if name:
                match session.bind.dialect.name:
                    case "postgres":
                        query = query.where(
                            or_(
                                func.to_tsvector("english", SQLUser.name).op("@@")(
                                    func.plainto_tsquery("english", name)
                                ),
                                func.lower(SQLUser.name).contains(name.lower()),
                            )
                        )
                    case _:
                        query = query.where(func.lower(SQLUser.name).contains(name.lower()))
            if skip:
                query = query.offset(skip)
            if limit:
                query = query.limit(limit)

            if sort_by:
                match sort_by:
                    case (User.SortField.NAME, "asc"):
                        query = query.order_by(asc(SQLUser.name))
                    case (User.SortField.NAME, "desc"):
                        query = query.order_by(desc(SQLUser.name))
                    case (User.SortField.EMAIL, "asc"):
                        query = query.order_by(asc(SQLUser.email))
                    case (User.SortField.EMAIL, "desc"):
                        query = query.order_by(desc(SQLUser.email))
                    case (User.SortField.ROLE, "asc"):
                        query = query.order_by(asc(SQLUser.role), asc(SQLUser.name))
                    case (User.SortField.ROLE, "desc"):
                        query = query.order_by(desc(SQLUser.role), asc(SQLUser.name))

            results = (await session.execute(query)).scalars().all()
            self.logger.debug(
                "list_users returned", name=name, sort_by=sort_by, skip=skip, limit=limit, count=len(results)
            )
            return (r.as_common_type for r in results)

    async def _get_user(self, user_id: str, session: AsyncSession) -> SQLUser | None:
        self.logger.debug("_get_user query", user_id=user_id)
        if user := (await session.execute(select(SQLUser).where(SQLUser.id == user_id))).scalar_one_or_none():
            return user

        return None

    async def get_user(self, user_id_or_email: str) -> tuple[User, str] | None:
        async with self.session_factory() as session:
            if user := (
                await session.execute(
                    select(SQLUser).where(or_(SQLUser.id == user_id_or_email, SQLUser.email == user_id_or_email))
                )
            ).scalar_one_or_none():
                self.logger.debug("get_user succeeded", user_id=user_id_or_email)
                return user.as_common_type, user.password

            self.logger.debug("get_user no result", user_id=user_id_or_email)
            return None

    async def create_user(self, user_data: UserBaseData, password: str) -> User:
        async with self.session_factory() as session:
            user = SQLUser(
                name=user_data.name,
                email=user_data.email,
                password=password,
                role=user_data.role,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            created = user.as_common_type
            self.logger.info("create_user succeeded", user_id=created.id)
            return created

    async def update_user(self, user_id: str, user_data: UserUpdateData) -> User | None:
        async with self.session_factory() as session:
            if not (user := await self._get_user(user_id, session)):
                self.logger.warning("update_user failed; not found", user_id=user_id)
                return None

            for field, data in user_data.model_dump().items():
                if data:
                    setattr(user, field, data)

            await session.commit()
            await session.refresh(user)
            updated = user.as_common_type
            self.logger.info(
                "update_user succeeded",
                user_id=updated.id,
                fields=list(k for k, v in user_data.model_dump().items() if v),
            )
            return updated

    async def delete_user(self, user_id: str) -> User | None:
        async with self.session_factory() as session:
            if not (user := await self._get_user(user_id, session)):
                self.logger.warning("delete_user failed; not found", user_id=user_id)
                return None

            await session.delete(user)
            await session.commit()
            deleted = user.as_common_type
            self.logger.info("delete_user succeeded", user_id=deleted.id)
            return deleted
