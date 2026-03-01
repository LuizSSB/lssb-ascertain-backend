from datetime import date
from typing import Dict
from uuid import uuid4

import pytest

from app.data.patient import PatientRepository
from app.models.patient import Patient, PatientBaseData, PatientUpdateData
from app.models.utils import SortFieldData
from app.tooling.logging import AppLogger
from app.usecases.patient import PatientUsecases


class DummyPatientRepository(PatientRepository):
    def __init__(self) -> None:
        self._store: Dict[str, Patient] = {}

    async def list_patients(
        self,
        *,
        name: str | None = None,
        sort_by: SortFieldData[Patient.SortField] | None = None,
        skip: int | None = None,
        limit: int | None = None
    ):
        items = list(self._store.values())
        if skip:
            items = items[skip:]
        if limit:
            items = items[:limit]
        return (p for p in items)

    async def get_patient(self, patient_id: str) -> Patient | None:
        return self._store.get(patient_id)

    async def create_patient(self, patient_data: PatientBaseData) -> Patient:
        pid = str(uuid4())
        p = Patient(id=pid, name=patient_data.name, birthdate=patient_data.birthdate)
        self._store[pid] = p
        return p

    async def update_patient(self, patient_id: str, patient_data: PatientUpdateData) -> Patient | None:
        if patient_id not in self._store:
            return None
        p = self._store[patient_id]
        if patient_data.name:
            p.name = patient_data.name
        if patient_data.birthdate:
            p.birthdate = patient_data.birthdate
        self._store[patient_id] = p
        return p

    async def delete_patient(self, patient_id: str) -> Patient | None:
        return self._store.pop(patient_id, None)


@pytest.mark.asyncio
async def test_patient_usecases_list_and_crud(logger: AppLogger) -> None:
    repo = DummyPatientRepository()
    svc = PatientUsecases(repo, logger)

    # create
    p1 = await svc.create_patient(PatientBaseData(name="A", birthdate=date(1990, 1, 1)))
    await svc.create_patient(PatientBaseData(name="B", birthdate=date(1980, 1, 1)))

    # list with limit to trigger next token
    patients, next_token = await svc.list_patients(limit=1)
    assert len(patients) == 1
    assert next_token is not None

    # get
    got = await svc.get_patient(p1.id)
    assert got is not None and got.id == p1.id

    # update
    updated = await svc.update_patient(p1.id, PatientUpdateData(name="A-updated"))
    assert updated is not None and updated.name == "A-updated"

    # delete
    deleted = await svc.delete_patient(p1.id)
    assert deleted is not None and deleted.id == p1.id
    assert deleted is not None and deleted.id == p1.id
