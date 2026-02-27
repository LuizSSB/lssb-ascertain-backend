from datetime import date

from data.patient_note import PatientNoteRepository
from models.patient_note import PatientNote, PatientNoteBaseData
from models.utils import SkipNextToken, SortOrder


class PatientNoteUsecases:

    def __init__(self, repository: PatientNoteRepository) -> None:
        self.repository = repository

    async def list_notes(
        self,
        patient_id: str,
        *,
        sort_order: SortOrder | None = None,
        next_token: SkipNextToken | None = None,
        limit: int | None = None
    ) -> tuple[list[PatientNote], SkipNextToken | None]:
        skip = next_token.skip if next_token else 0
        notes = await self.repository.list_notes(patient_id, sort_order=sort_order, limit=limit, skip=skip)
        notes_list = list(notes)
        return (
            notes_list,
            SkipNextToken(skip=skip + len(notes_list)) if limit and len(notes_list) >= limit else None,
        )

    async def create_note(self, patient_id: str, soap_note: str) -> PatientNote:
        note_data = PatientNoteBaseData(
            patient_id=patient_id,
            assessment="TODO",
            encounter_date=date.fromisoformat("2023-01-01"),
            subjective="TODO",
            objective="TODO",
            physician="TODO",
            plan="TODO",
        )
        return await self.repository.create_note(note_data)

    async def delete_note(self, note_id: str) -> PatientNote | None:
        return await self.repository.delete_note(note_id)
