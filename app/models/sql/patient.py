import uuid
from datetime import date

from sqlmodel import Field, SQLModel

from app.models.patient import Patient


class SQLPatient(SQLModel, table=True):
    __tablename__ = "patients"  # type: ignore

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    name: str
    birthdate: date

    @property
    def as_common_type(self) -> Patient:
        return Patient(
            id=self.id,
            name=self.name,
            birthdate=self.birthdate,
        )
