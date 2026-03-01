from pathlib import Path
from typing import Any, List

import pytest

from app.data.patient_note import PatientNoteRepository
from app.models.patient_note import PatientNote, PatientNoteBaseData
from app.models.utils import SortOrder
from app.services.file_conversion import FileConversionService
from app.tooling.logging import AppLogger
from app.usecases.patient_note import PatientNoteUsecases
from tests.dummies.upload import DummyUploadFile


class DummyNoteRepository(PatientNoteRepository):
    def __init__(self) -> None:
        self._store: List[PatientNote] = []

    async def list_notes(
        self, patient_id: str, *, sort_order: SortOrder | None = None, skip: int | None = None, limit: int | None = None
    ):
        items = [n for n in self._store if n.patient_id == patient_id]
        if sort_order == "asc":
            items.sort(key=lambda n: n.encounter_date)
        elif sort_order == "desc":
            items.sort(key=lambda n: n.encounter_date, reverse=True)
        if skip:
            items = items[skip:]
        if limit:
            items = items[:limit]
        return (n for n in items)

    async def create_note(self, note_data: PatientNoteBaseData) -> PatientNote:
        note = PatientNote(id=str(len(self._store) + 1), **note_data.model_dump())
        self._store.append(note)
        return note

    async def delete_note(self, note_id: str) -> PatientNote | None:
        for i, n in enumerate(self._store):
            if n.id == note_id:
                return self._store.pop(i)
        return None


class DummyFileConversionService(FileConversionService):
    def __init__(self, text: str) -> None:
        self._text = text

    async def convert_to_text(self, file: Any) -> str:
        return self._text


@pytest.mark.asyncio
async def test_patient_note_usecases_get_soap_and_create_and_list_and_delete(logger: AppLogger) -> None:
    # read a sample SOAP-like note from test assets
    path = Path(__file__).parent.parent / "assets" / "notes" / "valid.txt"
    text = path.read_text()

    repo = DummyNoteRepository()
    file_conv = DummyFileConversionService(text)
    svc = PatientNoteUsecases(file_conv, repo, logger)

    # create note (uses convert_to_text + parsing)
    created = await svc.create_note("patient-1", file=DummyUploadFile.new())
    assert created.id is not None

    # list notes
    notes = await svc.list_notes("patient-1", limit=10)
    listed, _ = notes
    assert len(listed) >= 1

    # delete
    deleted = await svc.delete_note(created.id)
    assert deleted is not None

    # test _get_soap_note directly (parsing)
    soap = svc._get_soap_note(text)  # type: ignore
    assert soap.s is not None and soap.o is not None and soap.a is not None and soap.p is not None
