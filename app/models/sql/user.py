import uuid

from sqlmodel import Field, SQLModel

from app.models.user import User, UserRole


class SQLUser(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str = Field(unique=True, index=True)
    password: str
    role: UserRole

    @property
    def as_common_type(self) -> User:
        return User(
            id=self.id,
            name=self.name,
            email=self.email,
            role=self.role,
        )
