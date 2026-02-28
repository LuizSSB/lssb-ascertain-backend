from dependency_injector import providers

from app.data.patient.sql import SQLPatientRepository
from app.data.patient_note.sql import SQLPatientNoteRepository
from app.data.sqldatabase import SQLDatabase
from app.ioc.containers import BaseAppContainer
from app.models.app_settings import AppSettings
from app.usecases.patient import PatientUsecases
from app.usecases.patient_note import PatientNoteUsecases


class DefaultAppContainer(BaseAppContainer):
    db = providers.Singleton(
        SQLDatabase,
        db_url=AppSettings.default().DB_URL,
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
