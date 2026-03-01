from enum import Enum
from typing import Literal, TypeVar


_TField = TypeVar("_TField", bound=Enum)

SortOrder = Literal["asc", "desc"]
SortFieldData = tuple[_TField, SortOrder]
