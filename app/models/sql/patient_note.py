import uuid
from datetime import date

from sqlmodel import Field, SQLModel

from app.models.patient_note import PatientNote


class SQLPatientNote(SQLModel, table=True):
    __tablename__ = "patient_notes" # type: ignore

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = Field(foreign_key="patients.id")
    encounter_date: date
    subjective: str
    objective: str
    assessment: str
    plan: str
    physician: str

    @property
    def as_common_type(self):
        return PatientNote(
            id=self.id,
            patient_id=self.patient_id,
            encounter_date=self.encounter_date,
            subjective=self.subjective,
            objective=self.objective,
            assessment=self.assessment,
            plan=self.plan,
            physician=self.physician,
        )
