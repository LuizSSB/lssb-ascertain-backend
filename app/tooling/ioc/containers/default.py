from dependency_injector import providers
from langchain_openai import ChatOpenAI

from app.data.patient.sql import SQLPatientRepository
from app.data.patient_note.sql import SQLPatientNoteRepository
from app.data.sqldatabase import SQLDatabase
from app.data.user.sql import SQLUserRepository
from app.models.app_settings import AppSettings
from app.services.auth.default import DefaultAuthService
from app.services.file_conversion.default import DefaultFileConversionService
from app.services.summarization.deepagents import DeepAgentsSummarizationService
from app.tooling.ioc.containers import AppContainer
from app.tooling.logging import AppLogger
from app.tooling.logging.structlog import StructlogAppLogger
from app.usecases.auth import AuthUsecases
from app.usecases.patient import PatientUsecases
from app.usecases.patient_note import PatientNoteUsecases
from app.usecases.patient_summary import PatientSummaryUsecases
from app.usecases.user import UserUsecases


def _make_dependency_logger(base: type) -> AppLogger:
    return StructlogAppLogger(base.__name__)


class DefaultAppContainer(AppContainer):
    logger = providers.Factory(StructlogAppLogger)

    # data

    db = providers.Singleton(
        SQLDatabase,
        db_url=AppSettings.default().DB_URL,
        logger=_make_dependency_logger(SQLDatabase),
    )

    user_repository = providers.Factory(
        SQLUserRepository,
        session_factory=db.provided.session,
        logger=_make_dependency_logger(SQLUserRepository),
    )

    patient_repository = providers.Factory(
        SQLPatientRepository,
        session_factory=db.provided.session,
        logger=_make_dependency_logger(SQLPatientRepository),
    )

    patient_note_repository = providers.Factory(
        SQLPatientNoteRepository,
        session_factory=db.provided.session,
        logger=_make_dependency_logger(SQLPatientNoteRepository),
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
        logger=_make_dependency_logger(DefaultFileConversionService),
    )

    summarization_service = providers.Singleton(
        DeepAgentsSummarizationService,
        model=ai_model,
        logger=_make_dependency_logger(DeepAgentsSummarizationService),
    )

    auth_service = providers.Singleton(
        DefaultAuthService,
        logger=_make_dependency_logger(DefaultAuthService),
    )

    # usecases

    user_usecases = providers.Factory(
        UserUsecases,
        repository=user_repository,
        logger=_make_dependency_logger(UserUsecases),
    )

    auth_usecases = providers.Factory(
        AuthUsecases,
        user_repository=user_repository,
        auth_service=auth_service,
        logger=_make_dependency_logger(AuthUsecases),
    )

    patient_usecases = providers.Factory(
        PatientUsecases,
        repository=patient_repository,
        logger=_make_dependency_logger(PatientUsecases),
    )

    patient_note_usecases = providers.Factory(
        PatientNoteUsecases,
        file_conversion_service=file_conversion_service,
        repository=patient_note_repository,
        logger=_make_dependency_logger(PatientNoteUsecases),
    )

    patient_summary_usecases = providers.Factory(
        PatientSummaryUsecases,
        patient_repository=patient_repository,
        patient_note_repository=patient_note_repository,
        summarization_service=summarization_service,
        logger=_make_dependency_logger(PatientSummaryUsecases),
    )

    async def lifecycle_setup(self):
        await self.db().create_database()
