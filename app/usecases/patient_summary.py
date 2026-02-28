from app.data.patient import PatientRepository
from app.data.patient_note import PatientNoteRepository
from app.models.ai.summary import SummaryAudience, SummaryLength
from app.models.exceptions import NotFoundException
from app.models.patient_summary import PatientSummary
from app.services.summarization import SummarizationService


class PatientSummaryUsecases:
    def __init__(
        self,
        patient_repository: PatientRepository,
        patient_note_repository: PatientNoteRepository,
        summarization_service: SummarizationService,
    ):
        self.patient_repository = patient_repository
        self.patient_note_repository = patient_note_repository
        self.summarization_service = summarization_service

    async def summarize(self, patient_id: str, *, audience: SummaryAudience, length: SummaryLength) -> PatientSummary:
        if not (patient := await self.patient_repository.get_patient(patient_id)):
            raise NotFoundException()

        notes = await self.patient_note_repository.list_notes(patient_id, limit=10)
        summary = self.summarization_service.summarize_patient(
            patient, notes=list(notes), audience=audience, length=length
        )
        return PatientSummary(
            header=f"Patient: {patient.id} {patient.name} (born {patient.birthdate.isoformat()})", summary=summary
        )
