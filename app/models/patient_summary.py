from pydantic import BaseModel


class PatientSummary(BaseModel):
    header: str
    summary: str
