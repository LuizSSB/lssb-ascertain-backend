from datetime import date

from pydantic import BaseModel, Field


class SOAPNote(BaseModel):
    encounter_date: date = Field(description="Encounter date for the note")
    s: str = Field(description="Content of the S field: the patient's reported symptoms and history")
    o: str = Field(description="Content of the O field: the clinician's observations, exam findings, and test results")
    a: str = Field(description="Content of the A field: the clinician's diagnoses or summary of the case")
    p: str = Field(description="Content of the P field: the treatment plan or next steps for the patient")
    signed: str = Field(description="Name of the physician who signed the note")
