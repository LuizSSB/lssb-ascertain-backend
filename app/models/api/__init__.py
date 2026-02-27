from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


class ListRequest(BaseModel):
    next_token: str | None = None
    limit: int | None = None


_TData = TypeVar("_TData", bound=BaseModel)


class ListResponse(BaseModel, Generic[_TData]):
    next_token: str | None = None
    data: list[_TData]


class EntityResponse(BaseModel, Generic[_TData]):
    data: _TData


class ErrorResponse(BaseModel):
    message: str
    cause: Exception | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
