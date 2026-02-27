from data.patient.sql import SQLPatientRepository
from data.sqldatabase import SQLDatabase
from dependency_injector import containers, providers
from models.settings import AppSettings
from usecases.patient import PatientUsecases


class Container(containers.DeclarativeContainer):
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
