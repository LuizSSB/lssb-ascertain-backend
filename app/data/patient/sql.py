from contextlib import AbstractAsyncContextManager
from typing import Callable, Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import asc, col, desc, select

from app.data.patient import PatientRepository
from app.logging import AppLogger
from app.models.patient import Patient, PatientBaseData, PatientUpdateData
from app.models.sql.patient import SQLPatient
from app.models.utils import SortFieldData


class SQLPatientRepository(PatientRepository):

    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]], logger: AppLogger
    ) -> None:
        self.session_factory = session_factory
        self.logger = logger

    async def list_patients(
        self,
        *,
        name: str | None = None,
        sort_by: SortFieldData[Patient.SortField] | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Iterable[Patient]:
        self.logger.debug("list_patients called", name=name, sort_by=sort_by, skip=skip, limit=limit)
        query = select(SQLPatient)
        if name:
            query = query.where(col(SQLPatient.name).contains(name))
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

            query = query.order_by(order_function(order_field))

        async with self.session_factory() as session:
            results = (await session.execute(query)).scalars().all()
            self.logger.debug(
                "list_patients returned", name=name, sort_by=sort_by, skip=skip, limit=limit, count=len(results)
            )
            return (r.as_common_type for r in results)

    async def _get_patient(self, patient_id: str, session: AsyncSession) -> SQLPatient | None:
        self.logger.debug("_get_patient query", patient_id=patient_id)
        if patient := (
            await session.execute(select(SQLPatient).where(SQLPatient.id == patient_id))
        ).scalar_one_or_none():
            return patient

        return None

    async def get_patient(self, patient_id: str) -> Patient | None:
        async with self.session_factory() as session:
            if patient := await self._get_patient(patient_id, session):
                self.logger.debug("get_patient succeeded", patient_id=patient_id)
                return patient.as_common_type

            self.logger.debug("get_patient no result", patient_id=patient_id)
            return None

    async def create_patient(self, patient_data: PatientBaseData) -> Patient:
        async with self.session_factory() as session:
            patient = SQLPatient(name=patient_data.name, birthdate=patient_data.birthdate)
            session.add(patient)
            await session.commit()
            await session.refresh(patient)
            created = patient.as_common_type
            self.logger.info("create_patient succeeded", patient_id=created.id)
            return created

    async def update_patient(self, patient_id: str, patient_data: PatientUpdateData) -> Patient | None:
        async with self.session_factory() as session:
            if not (patient := await self._get_patient(patient_id, session)):
                self.logger.warning("update_patient failed; not found", patient_id=patient_id)
                return None

            for field, data in patient_data.model_dump().items():
                if data:
                    setattr(patient, field, data)

            await session.commit()
            await session.refresh(patient)
            updated = patient.as_common_type
            self.logger.info(
                "update_patient succeeded",
                patient_id=updated.id,
                fields=list(k for k, v in patient_data.model_dump().items() if v),
            )
            return updated

    async def delete_patient(self, patient_id: str) -> Patient | None:
        async with self.session_factory() as session:
            if not (patient := await self._get_patient(patient_id, session)):
                self.logger.warning("delete_patient failed; not found", patient_id=patient_id)
                return None

            await session.delete(patient)
            await session.commit()
            deleted = patient.as_common_type
            self.logger.info("delete_patient succeeded", patient_id=deleted.id)
            return deleted
