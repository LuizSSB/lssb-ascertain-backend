from datetime import date

import pytest

from app.data.patient.sql import SQLPatientRepository
from app.data.sqldatabase import SQLDatabase
from app.models.patient import Patient, PatientBaseData, PatientUpdateData
from app.tooling.logging import AppLogger


@pytest.mark.asyncio
async def test_sql_patient_repository_crud(database: SQLDatabase, logger: AppLogger) -> None:
    repo = SQLPatientRepository(database.session, logger)

    # create & get
    alice_in = PatientBaseData(name="Alice", birthdate=date(1990, 1, 1))
    created = await repo.create_patient(alice_in)
    assert created.id
    assert created.name == alice_in.name
    assert created.birthdate == alice_in.birthdate

    fetched = await repo.get_patient(created.id)
    assert fetched is not None
    assert fetched.id == created.id

    # update
    updated = await repo.update_patient(created.id, PatientUpdateData(name="Alicia"))
    assert updated is not None
    assert updated.name == "Alicia"

    # delete
    deleted = await repo.delete_patient(created.id)
    assert deleted is not None
    assert deleted.id == created.id

    fetched_after = await repo.get_patient(created.id)
    assert fetched_after is None


@pytest.mark.asyncio
async def test_sql_patient_repository_list_sort_filter_skip_limit(database: SQLDatabase, logger: AppLogger) -> None:
    repo = SQLPatientRepository(database.session, logger)

    patients = [
        PatientBaseData(name="Alice", birthdate=date(1990, 1, 1)),
        PatientBaseData(name="Bob", birthdate=date(1985, 5, 5)),
        PatientBaseData(name="Charlie", birthdate=date(2000, 12, 12)),
    ]

    [await repo.create_patient(p) for p in patients]

    # list all
    all_gen = await repo.list_patients()
    all_list = list(all_gen)
    assert len(all_list) >= 3

    # filter by name substring
    filtered_gen = await repo.list_patients(name="Ali")
    filtered = list(filtered_gen)
    assert any(p.name == "Alice" for p in filtered)

    # sort by name asc
    sorted_gen = await repo.list_patients(sort_by=(Patient.SortField.NAME, "asc"))
    sorted_list = list(sorted_gen)
    names = [p.name for p in sorted_list]
    assert names == sorted(names)

    # sort by birthdate desc
    sorted_bd_gen = await repo.list_patients(sort_by=(Patient.SortField.BIRTHDATE, "desc"))
    sorted_bd = list(sorted_bd_gen)
    bds = [p.birthdate for p in sorted_bd]
    assert bds == sorted(bds, reverse=True)

    # skip & limit
    skip_limit_gen = await repo.list_patients(sort_by=(Patient.SortField.NAME, "asc"), skip=1, limit=1)
    skip_limit = list(skip_limit_gen)
    assert len(skip_limit) <= 1


@pytest.mark.asyncio
async def test_sql_patient_repository_update_delete_nonexistent(database: SQLDatabase, logger: AppLogger) -> None:
    repo = SQLPatientRepository(database.session, logger)

    updated = await repo.update_patient("nonexistent-id", PatientUpdateData(name="Nope"))
    assert updated is None

    deleted = await repo.delete_patient("nonexistent-id")
    assert deleted is None
