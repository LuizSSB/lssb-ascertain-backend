from datetime import date

from pydantic import BaseModel

from app.models.utils import SortOrder


class PatientNoteBaseData(BaseModel):
    patient_id: str
    encounter_date: date
    subjective: str
    objective: str
    assessment: str
    plan: str
    physician: str


class PatientNote(PatientNoteBaseData):
    id: str


class PatientNoteNextToken(BaseModel):
    skip: int
    sort_order: SortOrder

    def __str__(self) -> str:
        return self.model_dump_json()
