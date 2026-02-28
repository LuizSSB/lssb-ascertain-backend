from dependency_injector import providers
from langchain_openai import ChatOpenAI

from app.data.patient.sql import SQLPatientRepository
from app.data.patient_note.sql import SQLPatientNoteRepository
from app.data.sqldatabase import SQLDatabase
from app.ioc.containers import BaseAppContainer
from app.models.app_settings import AppSettings
from app.services.file_conversion.default import DefaultFileConversionService
from app.services.summarization.deep_agents import DeepAgentsSummarizationService
from app.usecases.patient import PatientUsecases
from app.usecases.patient_note import PatientNoteUsecases
from app.usecases.patient_summary import PatientSummaryUsecases


class DefaultAppContainer(BaseAppContainer):
    # data

    db = providers.Singleton(
        SQLDatabase,
        db_url=AppSettings.default().DB_URL,
    )

    patient_repository = providers.Factory(
        SQLPatientRepository,
        session_factory=db.provided.session,
    )

    patient_note_repository = providers.Factory(
        SQLPatientNoteRepository,
        session_factory=db.provided.session,
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
    )

    summarization_service = providers.Singleton(
        DeepAgentsSummarizationService,
    )

    # usecases

    patient_usecases = providers.Factory(
        PatientUsecases,
        repository=patient_repository,
    )

    patient_note_usecases = providers.Factory(
        PatientNoteUsecases,
        file_conversion_service=file_conversion_service,
        repository=patient_repository,
    )

    patient_summary_usecases = providers.Factory(
        PatientSummaryUsecases,
        patient_repository=patient_repository,
        patient_note_repository=patient_note_repository,
        summarization_service=summarization_service,
    )

    async def lifecycle_setup(self):
        await self.db().create_database()
