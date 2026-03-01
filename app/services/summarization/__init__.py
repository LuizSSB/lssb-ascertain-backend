from abc import ABC, abstractmethod

from app.models.summary import SummaryAudience, SummaryLength
from app.models.patient import Patient
from app.models.patient_note import PatientNote


class SummarizationService(ABC):
    @abstractmethod
    def summarize_patient(
        self, patient: Patient, *, notes: list[PatientNote], audience: SummaryAudience, length: SummaryLength
    ) -> str:
        pass
