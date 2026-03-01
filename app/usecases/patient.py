from app.data.patient import PatientRepository
from app.models.patient import Patient, PatientBaseData, PatientNextToken, PatientUpdateData
from app.tooling.logging import AppLogger


class PatientUsecases:

    def __init__(self, repository: PatientRepository, logger: AppLogger) -> None:
        self.repository = repository
        self.logger = logger

    async def list_patients(
        self, *, next_token: PatientNextToken | None = None, limit: int | None = None
    ) -> tuple[list[Patient], PatientNextToken | None]:
        self.logger.debug("list_patients usecase", next_token=next_token, limit=limit)

        next_token = next_token or PatientNextToken(skip=0)
        patients = list(
            await self.repository.list_patients(
                name=next_token.search_term,
                sort_by=(next_token.sort_field, next_token.sort_order or "asc") if next_token.sort_field else None,
                skip=next_token.skip,
                limit=limit,
            )
        )

        if limit and len(patients) >= limit:
            next_next_token = next_token.model_copy()
            next_next_token.skip += len(patients)
        else:
            next_next_token = None

        self.logger.debug("list_patients returned", next_token=next_token, limit=limit, next_next_token=next_next_token)
        return patients, next_next_token

    async def get_patient(self, patient_id: str) -> Patient | None:
        self.logger.debug("get_patient usecase", patient_id=patient_id)
        return await self.repository.get_patient(patient_id)

    async def create_patient(self, patient_data: PatientBaseData) -> Patient:
        self.logger.debug("create_patient usecase", patient_data=patient_data.model_dump())
        return await self.repository.create_patient(patient_data)

    async def update_patient(self, patient_id: str, patient_data: PatientUpdateData) -> Patient | None:
        self.logger.debug("update_patient usecase", patient_id=patient_id, patient_data=patient_data.model_dump())
        return await self.repository.update_patient(patient_id, patient_data)

    async def delete_patient(self, patient_id: str) -> Patient | None:
        self.logger.debug("delete_patient usecase", patient_id=patient_id)
        return await self.repository.delete_patient(patient_id)
