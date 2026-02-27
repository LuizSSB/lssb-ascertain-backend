from enum import Enum
from typing import Literal, TypeVar

from pydantic import BaseModel

_TField = TypeVar("_TField", bound=Enum)

SortOrder = Literal["asc", "desc"]
SortFieldData = tuple[_TField, SortOrder]


class SkipNextToken(BaseModel):
    skip: int

    @staticmethod
    def from_string(token: str) -> "SkipNextToken":
        return SkipNextToken.model_validate_json(token)

    def __repr__(self) -> str:
        return self.model_dump_json()
