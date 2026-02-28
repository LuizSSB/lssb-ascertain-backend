from dependency_injector import containers, providers

from app.data.patient import PatientRepository
from app.data.patient_note import PatientNoteRepository
from app.usecases.patient import PatientUsecases
from app.usecases.patient_note import PatientNoteUsecases


class BaseAppContainer(containers.DeclarativeContainer):
    patient_repository: providers.Provider[PatientRepository]

    patient_usecases = providers.Provider[PatientUsecases]

    patient_note_repository = providers.Provider[PatientNoteRepository]

    patient_note_usecases = providers.Provider[PatientNoteUsecases]

    async def lifecycle_setup(self):
        pass
