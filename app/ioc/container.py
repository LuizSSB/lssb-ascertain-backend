from data.patient import PatientRepository
from data.patient.sql import SQLPatientRepository
from data.patient_note import PatientNoteRepository
from data.patient_note.sql import SQLPatientNoteRepository
from data.sqldatabase import SQLDatabase
from dependency_injector import containers, providers
from models.settings import AppSettings
from usecases.patient import PatientUsecases
from usecases.patient_note import PatientNoteUsecases


class Container(containers.DeclarativeContainer):
    db = providers.Singleton(
        SQLDatabase,
        db_url=AppSettings.default().db_url,
    )

    patient_repository = providers.Factory[PatientRepository](
        SQLPatientRepository,
        session_factory=db.provided.session,
    )

    patient_usecases = providers.Factory(
        PatientUsecases,
        repository=patient_repository,
    )

    patient_note_repository = providers.Factory[PatientNoteRepository](
        SQLPatientNoteRepository,
        session_factory=db.provided.session,
    )

    patient_note_usecases = providers.Factory(
        PatientNoteUsecases,
        repository=patient_repository,
    )
