from datetime import date

from pydantic import BaseModel


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
