from datetime import date

import pytest

from app.data.patient.sql import SQLPatientRepository
from app.data.sqldatabase import SQLDatabase
from app.models.patient import PatientBaseData, PatientUpdateData
from app.tooling.logging import AppLogger


@pytest.mark.asyncio
async def test_patient_crud(database: SQLDatabase, logger: AppLogger) -> None:
    repo: SQLPatientRepository = SQLPatientRepository(database.session, logger)

    created = await repo.create_patient(PatientBaseData(name="Alice", birthdate=date(1990, 1, 1)))
    assert created.id is not None

    got = await repo.get_patient(created.id)
    assert got is not None and got.id == created.id

    listed = list(await repo.list_patients(name="Alice"))
    assert any(p.id == created.id for p in listed)

    updated = await repo.update_patient(created.id, PatientUpdateData(name="Alicia"))
    assert updated is not None and updated.name == "Alicia"

    deleted = await repo.delete_patient(created.id)
    assert deleted is not None and deleted.id == created.id

    assert await repo.get_patient(created.id) is None
