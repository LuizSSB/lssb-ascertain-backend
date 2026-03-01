from dependency_injector import containers, providers

from app.data.patient import PatientRepository
from app.data.patient_note import PatientNoteRepository
from app.services.file_conversion import FileConversionService
from app.services.summarization import SummarizationService
from app.usecases.patient import PatientUsecases
from app.usecases.patient_note import PatientNoteUsecases
from app.usecases.patient_summary import PatientSummaryUsecases


class AppContainer(containers.DeclarativeContainer):
    # data

    patient_repository: providers.Provider[PatientRepository]

    patient_note_repository: providers.Provider[PatientNoteRepository]

    # services

    file_conversion_service: providers.Provider[FileConversionService]

    summarization_service: providers.Provider[SummarizationService]

    # usecases

    patient_usecases: providers.Provider[PatientUsecases]

    patient_note_usecases: providers.Provider[PatientNoteUsecases]

    patient_summary_usecases: providers.Provider[PatientSummaryUsecases]

    async def lifecycle_setup(self):
        pass
