import uuid
from datetime import date

from models.patient import Patient
from models.sql import BaseSQLModel
from sqlalchemy import Date
from sqlalchemy.orm import Mapped, mapped_column


class SQLPatient(BaseSQLModel):
    __tablename__ = "patients"
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(nullable=False)
    birthdate: Mapped[date] = mapped_column(Date, nullable=False)

    @property
    def as_common_type(self) -> Patient:
        return Patient(
            id=self.id,
            name=self.name,
            birthdate=self.birthdate,
        )
