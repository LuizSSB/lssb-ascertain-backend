from typing import Generic, NotRequired, TypedDict, TypeVar

from pydantic import BaseModel


class ListRequest(BaseModel):
    next_token: str | None = None
    limit: int | None = None


_TData = TypeVar("_TData", bound=BaseModel)


class ListResponse(BaseModel, Generic[_TData]):
    next_token: str | None = None
    data: list[_TData]


class EntityResponse(BaseModel, Generic[_TData]):
    data: _TData


class ErrorResponse(TypedDict):
    message: str
    cause: NotRequired[str]
