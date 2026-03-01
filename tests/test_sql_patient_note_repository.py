from datetime import date

import pytest

from app.data.patient.sql import SQLPatientRepository
from app.data.patient_note.sql import SQLPatientNoteRepository
from app.data.sqldatabase import SQLDatabase
from app.models.patient import PatientBaseData
from app.models.patient_note import PatientNoteBaseData
from app.tooling.logging import AppLogger


@pytest.mark.asyncio
async def test_patient_note_crud(database: SQLDatabase, logger: AppLogger) -> None:
    patient_repo = SQLPatientRepository(database.session, logger)
    patient = await patient_repo.create_patient(PatientBaseData(name="Bob", birthdate=date(1985, 2, 2)))

    repo = SQLPatientNoteRepository(database.session, logger)

    note_data = PatientNoteBaseData(
        patient_id=patient.id,
        encounter_date=date(2024, 1, 1),
        subjective="subj",
        objective="obj",
        assessment="assess",
        plan="plan",
        physician="dr",
    )

    created = await repo.create_note(note_data)
    assert created.id is not None

    listed = list(await repo.list_notes(patient.id))
    assert any(n.id == created.id for n in listed)

    await repo.create_note(
        PatientNoteBaseData(
            patient_id=patient.id,
            encounter_date=date(2025, 1, 1),
            subjective="s2",
            objective="o2",
            assessment="a2",
            plan="p2",
            physician="dr2",
        )
    )

    asc_list = list(await repo.list_notes(patient.id, sort_order="asc"))
    desc_list = list(await repo.list_notes(patient.id, sort_order="desc"))
    assert asc_list[0].encounter_date <= asc_list[1].encounter_date
    assert desc_list[0].encounter_date >= desc_list[1].encounter_date

    deleted = await repo.delete_note(created.id)
    assert deleted is not None and deleted.id == created.id
