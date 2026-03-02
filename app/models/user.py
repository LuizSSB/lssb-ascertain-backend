from datetime import date
from enum import Enum

from pydantic import BaseModel

from app.models.utils import SortOrder


class UserRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"


class UserBaseData(BaseModel):
    name: str
    email: str
    role: UserRole


class User(UserBaseData):
    class SortField(str, Enum):
        NAME = "name"
        EMAIL = "email"
        ROLE = "ROLE"

    id: str


class UserUpdateData(BaseModel):
    name: str | None = None
    email: date | None = None
    role: UserRole | None = None


class UserNextToken(BaseModel):
    skip: int
    sort_field: User.SortField | None = None
    sort_order: SortOrder | None = None
    search_term: str | None = None

    def __str__(self) -> str:
        return self.model_dump_json()
