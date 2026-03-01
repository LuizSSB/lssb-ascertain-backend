from app.data.patient import PatientRepository
from app.data.patient_note import PatientNoteRepository
from app.models.ai.summary import SummaryAudience, SummaryLength
from app.models.exceptions import NotFoundException
from app.models.patient_summary import PatientSummary
from app.services.summarization import SummarizationService
from app.tooling.logging import AppLogger


class PatientSummaryUsecases:
    def __init__(
        self,
        patient_repository: PatientRepository,
        patient_note_repository: PatientNoteRepository,
        summarization_service: SummarizationService,
        logger: AppLogger,
    ):
        self.patient_repository = patient_repository
        self.patient_note_repository = patient_note_repository
        self.summarization_service = summarization_service
        self.logger = logger

    async def summarize(self, patient_id: str, *, audience: SummaryAudience, length: SummaryLength) -> PatientSummary:
        self.logger.debug("summarize usecase called", patient_id=patient_id, audience=audience.name, length=length.name)
        if not (patient := await self.patient_repository.get_patient(patient_id)):
            self.logger.error("summarize usecase patient not found", patient_id=patient_id)
            raise NotFoundException()

        notes = await self.patient_note_repository.list_notes(patient_id, limit=10)
        self.logger.debug(
            "summarize usecase retrieved notes",
            patient_id=patient_id,
            audience=audience.name,
            length=length.name,
            count=len(list(notes)),
        )
        summary = self.summarization_service.summarize_patient(
            patient, notes=list(notes), audience=audience, length=length
        )
        return PatientSummary(
            header=f"Patient: {patient.name} (id: {patient.id}, born {patient.birthdate.isoformat()})", summary=summary
        )
