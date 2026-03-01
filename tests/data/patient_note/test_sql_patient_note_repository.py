from datetime import date
from uuid import uuid4

import pytest

from app.data.patient.sql import SQLPatientRepository
from app.data.patient_note.sql import SQLPatientNoteRepository
from app.data.sqldatabase import SQLDatabase
from app.models.patient import Patient
from app.models.patient_note import PatientNoteBaseData
from app.tooling.logging import AppLogger


@pytest.mark.asyncio
async def test_sql_patient_note_repository_crud(database: SQLDatabase, logger: AppLogger) -> None:
    patient_id = str(uuid4())
    patient_repo = SQLPatientRepository(database.session, logger)
    await patient_repo.create_patient(Patient(id=patient_id, name="foobar", birthdate=date(2000, 2, 2)))

    repo = SQLPatientNoteRepository(database.session, logger)

    notes = [
        PatientNoteBaseData(
            patient_id=patient_id,
            encounter_date=date(2021, 1, 1),
            subjective="S1",
            objective="O1",
            assessment="A1",
            plan="P1",
            physician="Dr. A",
        ),
        PatientNoteBaseData(
            patient_id=patient_id,
            encounter_date=date(2022, 2, 2),
            subjective="S2",
            objective="O2",
            assessment="A2",
            plan="P2",
            physician="Dr. B",
        ),
        PatientNoteBaseData(
            patient_id=patient_id,
            encounter_date=date(2020, 3, 3),
            subjective="S3",
            objective="O3",
            assessment="A3",
            plan="P3",
            physician="Dr. C",
        ),
    ]

    created = [await repo.create_note(n) for n in notes]
    assert len(created) == 3

    # list all
    gen_all = await repo.list_notes(patient_id)
    all_notes = list(gen_all)
    assert len(all_notes) >= 3

    # list with sort asc
    gen_asc = await repo.list_notes(patient_id, sort_order="asc")
    asc_notes = list(gen_asc)
    dates_asc = [n.encounter_date for n in asc_notes]
    assert dates_asc == sorted(dates_asc)

    # list with sort desc
    gen_desc = await repo.list_notes(patient_id, sort_order="desc")
    desc_notes = list(gen_desc)
    dates_desc = [n.encounter_date for n in desc_notes]
    assert dates_desc == sorted(dates_desc, reverse=True)

    # skip & limit
    gen_skip_limit = await repo.list_notes(patient_id, skip=1, limit=1)
    skip_limit = list(gen_skip_limit)
    assert len(skip_limit) <= 1

    # delete one
    to_delete = created[0]
    deleted = await repo.delete_note(to_delete.id)
    assert deleted is not None
    assert deleted.id == to_delete.id


@pytest.mark.asyncio
async def test_sql_patient_note_repository_delete_nonexistent(database: SQLDatabase, logger: AppLogger) -> None:
    repo = SQLPatientNoteRepository(database.session, logger)

    deleted = await repo.delete_note("nonexistent-note")
    assert deleted is None
