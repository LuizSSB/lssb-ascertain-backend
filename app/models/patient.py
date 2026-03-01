from datetime import date
from enum import Enum

from pydantic import BaseModel

from app.models.utils import SortOrder


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


class PatientNextToken(BaseModel):
    skip: int
    sort_field: Patient.SortField | None = None
    sort_order: SortOrder | None = None
    search_term: str | None = None

    def __str__(self) -> str:
        return self.model_dump_json()
