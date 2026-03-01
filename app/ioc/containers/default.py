from uuid import uuid4

from dependency_injector import providers
from langchain_openai import ChatOpenAI

from app.data.patient.sql import SQLPatientRepository
from app.data.patient_note.sql import SQLPatientNoteRepository
from app.data.sqldatabase import SQLDatabase
from app.ioc.containers import AppContainer
from app.models.app_settings import AppSettings
from app.services.file_conversion.default import DefaultFileConversionService
from app.services.summarization.deepagents import DeepAgentsSummarizationService
from app.tooling.logging import AppLogger
from app.tooling.logging.structlog import StructlogAppLogger
from app.usecases.patient import PatientUsecases
from app.usecases.patient_note import PatientNoteUsecases
from app.usecases.patient_summary import PatientSummaryUsecases


def _make_logger(base: type) -> AppLogger:
    return StructlogAppLogger(_name=base.__name__, _id=str(uuid4()))


class DefaultAppContainer(AppContainer):
    # data

    db = providers.Singleton(
        SQLDatabase,
        db_url=AppSettings.default().DB_URL,
        logger=_make_logger(SQLDatabase),
    )

    patient_repository = providers.Factory(
        SQLPatientRepository,
        session_factory=db.provided.session,
        logger=_make_logger(SQLPatientRepository),
    )

    patient_note_repository = providers.Factory(
        SQLPatientNoteRepository,
        session_factory=db.provided.session,
        logger=_make_logger(SQLPatientNoteRepository),
    )

    # services

    ai_model = providers.Singleton(
        ChatOpenAI,
        openai_api_base=AppSettings.default().AI_OPENAI_API_BASE,
        openai_api_key=AppSettings.default().AI_OPENAI_API_KEY,
        model_name=AppSettings.default().AI_MODEL_NAME,
    )

    file_conversion_service = providers.Singleton(
        DefaultFileConversionService,
        logger=_make_logger(DefaultFileConversionService),
    )

    summarization_service = providers.Singleton(
        DeepAgentsSummarizationService,
        model=ai_model,
        logger=_make_logger(DeepAgentsSummarizationService),
    )

    # usecases

    patient_usecases = providers.Factory(
        PatientUsecases,
        repository=patient_repository,
        logger=_make_logger(PatientUsecases),
    )

    patient_note_usecases = providers.Factory(
        PatientNoteUsecases,
        file_conversion_service=file_conversion_service,
        repository=patient_note_repository,
        logger=_make_logger(PatientNoteUsecases),
    )

    patient_summary_usecases = providers.Factory(
        PatientSummaryUsecases,
        patient_repository=patient_repository,
        patient_note_repository=patient_note_repository,
        summarization_service=summarization_service,
        logger=_make_logger(PatientSummaryUsecases),
    )

    async def lifecycle_setup(self):
        await self.db().create_database()
