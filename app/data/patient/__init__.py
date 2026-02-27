from abc import ABC, abstractmethod
from typing import Iterable

from models.patient import Patient, PatientBaseData, PatientUpdateData
from models.utils import SortFieldData


class PatientRepository(ABC):

    @abstractmethod
    async def list_patients(
        self,
        *,
        name: str | None = None,
        sort_by: SortFieldData[Patient.SortField] | None = None,
        skip: int | None = None,
        limit: int | None = None
    ) -> Iterable[Patient]:
        pass

    @abstractmethod
    async def get_patient(self, patient_id: str) -> Patient | None:
        pass

    @abstractmethod
    async def create_patient(self, patient_data: PatientBaseData) -> Patient:
        pass

    @abstractmethod
    async def update_patient(self, patient_id: str, patient_data: PatientUpdateData) -> Patient | None:
        pass

    @abstractmethod
    async def delete_patient(self, patient_id: str) -> Patient | None:
        pass
