import uuid
from datetime import date

from models.patient_note import PatientNote
from models.sql import BaseSQLModel
from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class SQLPatientNote(BaseSQLModel):
    __tablename__ = "patient_notes"
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), nullable=False)
    encounter_date: Mapped[date] = mapped_column(Date, nullable=False)
    subjective: Mapped[str] = mapped_column(nullable=False)
    objective: Mapped[str] = mapped_column(nullable=False)
    assessment: Mapped[str] = mapped_column(nullable=False)
    plan: Mapped[str] = mapped_column(nullable=False)
    physician: Mapped[str] = mapped_column(nullable=False)

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
