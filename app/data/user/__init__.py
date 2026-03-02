from abc import ABC, abstractmethod
from typing import Iterable

from app.models.user import User, UserBaseData, UserUpdateData
from app.models.utils import SortFieldData


class UserRepository(ABC):

    @abstractmethod
    async def list_users(
        self,
        *,
        name: str | None = None,
        sort_by: SortFieldData[User.SortField] | None = None,
        skip: int | None = None,
        limit: int | None = None
    ) -> Iterable[User]:
        pass

    @abstractmethod
    async def get_user(self, user_id: str) -> User | None:
        pass

    @abstractmethod
    async def create_user(self, user_data: UserBaseData) -> User:
        pass

    @abstractmethod
    async def update_user(self, user_id: str, user_data: UserUpdateData) -> User | None:
        pass

    @abstractmethod
    async def delete_user(self, user_id: str) -> User | None:
        pass
