from data.patient.sql import SQLPatientRepository
from data.patient_note.sql import SQLPatientNoteRepository
from data.sqldatabase import SQLDatabase
from dependency_injector import providers
from ioc.containers import BaseAppContainer
from models.app_settings import AppSettings
from usecases.patient import PatientUsecases
from usecases.patient_note import PatientNoteUsecases


class DefaultAppContainer(BaseAppContainer):
    db = providers.Singleton(
        SQLDatabase,
        db_url=AppSettings.default().db_url,
    )

    patient_repository = providers.Factory(
        SQLPatientRepository,
        session_factory=db.provided.session,
    )

    patient_usecases = providers.Factory(
        PatientUsecases,
        repository=patient_repository,
    )

    patient_note_repository = providers.Factory(
        SQLPatientNoteRepository,
        session_factory=db.provided.session,
    )

    patient_note_usecases = providers.Factory(
        PatientNoteUsecases,
        repository=patient_repository,
    )

    async def lifecycle_setup(self):
        await self.db().create_database()
