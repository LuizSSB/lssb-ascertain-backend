from app.data.patient import PatientRepository
from app.models.patient import Patient, PatientBaseData, PatientUpdateData
from app.models.utils import SkipNextToken, SortFieldData


class PatientUsecases:

    def __init__(self, repository: PatientRepository) -> None:
        self.repository = repository

    async def list_patients(
        self,
        *,
        search_term: str | None = None,
        sort_by: SortFieldData[Patient.SortField] | None = None,
        next_token: SkipNextToken | None = None,
        limit: int | None = None
    ) -> tuple[list[Patient], SkipNextToken | None]:
        skip = next_token.skip if next_token else 0
        patients = await self.repository.list_patients(name=search_term, sort_by=sort_by, limit=limit, skip=skip)
        patients_list = list(patients)
        return (
            patients_list,
            SkipNextToken(skip=skip + len(patients_list)) if limit and len(patients_list) >= limit else None,
        )

    async def get_patient(self, patient_id: str) -> Patient | None:
        return await self.repository.get_patient(patient_id)

    async def create_patient(self, patient_data: PatientBaseData) -> Patient:
        return await self.repository.create_patient(patient_data)

    async def update_patient(self, patient_id: str, patient_data: PatientUpdateData) -> Patient | None:
        return await self.repository.update_patient(patient_id, patient_data)

    async def delete_patient(self, patient_id: str) -> Patient | None:
        return await self.repository.delete_patient(patient_id)
