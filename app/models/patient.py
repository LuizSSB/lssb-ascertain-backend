from datetime import date
from enum import Enum

from pydantic import BaseModel


class PatientBaseData(BaseModel):
    name: str
    birthdate: date


class Patient(PatientBaseData):
    class SortField(str, Enum):
        NAME = "name"
        BIRTHDATE = "birthdate"

    id: str


class PatientUpdateData(BaseModel):
    name: str | None = None
    birthdate: date | None = None
