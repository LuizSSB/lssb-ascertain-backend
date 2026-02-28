from abc import ABC, abstractmethod
from typing import Iterable

from app.models.patient_note import PatientNote, PatientNoteBaseData
from app.models.utils import SortOrder


class PatientNoteRepository(ABC):

    @abstractmethod
    async def list_notes(
        self, patient_id: str, *, sort_order: SortOrder | None = None, skip: int | None = None, limit: int | None = None
    ) -> Iterable[PatientNote]:
        pass

    @abstractmethod
    async def create_note(self, note_data: PatientNoteBaseData) -> PatientNote:
        pass

    @abstractmethod
    async def delete_note(self, note_id: str) -> PatientNote | None:
        pass
