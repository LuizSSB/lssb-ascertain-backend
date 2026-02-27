from contextlib import AbstractAsyncContextManager
from typing import Callable, Iterable

from data.patient import PatientRepository
from models.patient import Patient, PatientBaseData, PatientUpdateData
from models.sql.patient import SQLPatient
from models.utils import SortFieldData
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession


class SQLPatientRepository(PatientRepository):

    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]) -> None:
        self.session_factory = session_factory

    async def list_patients(
        self,
        *,
        name: str | None = None,
        sort_by: SortFieldData[Patient.SortField] | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Iterable[Patient]:
        query = select(SQLPatient)
        if name:
            query = query.filter(SQLPatient.name.like(f"%{name}%"))
        if skip:
            query = query.offset(skip)
        if limit:
            query = query.limit(limit)
        if sort_by:
            match sort_by[0]:
                case Patient.SortField.NAME:
                    order_field = SQLPatient.name
                case Patient.SortField.BIRTHDATE:
                    order_field = SQLPatient.birthdate

            match sort_by[1]:
                case "asc":
                    order_function = asc
                case "desc":
                    order_function = desc

            query.order_by(order_function(order_field))

        async with self.session_factory() as session:
            results = (await session.execute(query)).scalars().all()
            return (r.as_common_type for r in results)

    async def _get_patient(self, patient_id: str, session: AsyncSession) -> SQLPatient | None:
        if patient := (
            await session.execute(select(SQLPatient).filter(SQLPatient.id == patient_id))
        ).scalar_one_or_none():
            return patient

        return None

    async def get_patient(self, patient_id: str) -> Patient | None:
        async with self.session_factory() as session:
            return await self._get_patient(patient_id, session)

    async def create_patient(self, patient_data: PatientBaseData) -> Patient:
        async with self.session_factory() as session:
            patient = SQLPatient(name=patient_data.name, birthdate=patient_data.birthdate)
            session.add(patient)
            await session.commit()
            await session.refresh(patient)
            return patient.as_common_type

    async def update_patient(self, patient_id: str, patient_data: PatientUpdateData) -> Patient | None:
        async with self.session_factory() as session:
            if not (patient := await self._get_patient(patient_id, session)):
                return None

            for field, data in patient_data.model_dump().items():
                if data:
                    setattr(patient, field, data)

            await session.commit()
            await session.refresh(patient)
            return patient.as_common_type

    async def delete_patient(self, patient_id: str) -> Patient | None:
        async with self.session_factory() as session:
            if not (patient := await self._get_patient(patient_id, session)):
                return None

            await session.delete(patient)
            await session.commit()
            return patient.as_common_type
