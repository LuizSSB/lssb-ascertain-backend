import re

from pydantic import ValidationError
from starlette.datastructures import UploadFile

from app.data.patient_note import PatientNoteRepository
from app.models.ai.soap import SOAPNote
from app.models.patient_note import PatientNote, PatientNoteBaseData
from app.models.utils import SkipNextToken, SortOrder
from app.services.file_conversion import FileConversionService


class PatientNoteUsecases:

    def __init__(self, file_conversion_service: FileConversionService, repository: PatientNoteRepository) -> None:
        self.file_conversion_service = file_conversion_service
        self.repository = repository

    async def list_notes(
        self,
        patient_id: str,
        *,
        sort_order: SortOrder | None = None,
        next_token: SkipNextToken | None = None,
        limit: int | None = None,
    ) -> tuple[list[PatientNote], SkipNextToken | None]:
        skip = next_token.skip if next_token else 0
        notes = await self.repository.list_notes(patient_id, sort_order=sort_order, limit=limit, skip=skip)
        notes_list = list(notes)
        return (
            notes_list,
            SkipNextToken(skip=skip + len(notes_list)) if limit and len(notes_list) >= limit else None,
        )

    def _get_soap_note(self, note: str) -> SOAPNote:
        # Patterns to capture the specific sections
        # Using re.DOTALL to ensure '.' matches newlines within sections
        patterns = {
            "encounter_date": r"Encounter Date:\s*(\d{4}-\d{2}-\d{2})",
            "s": r"S:\s*(.*?)\s*O:",
            "o": r"O:\s*(.*?)\s*A:",
            "a": r"A:\s*(.*?)\s*P:",
            "p": r"P:\s*(.*?)\s*Signed:",
            "signed": r"Signed:\s*\n?\s*([^,\n]+)",
        }

        extracted_data = {}

        for field, pattern in patterns.items():
            match = re.search(pattern, note, re.DOTALL | re.IGNORECASE)

            if not match or not match.group(1).strip():
                raise ValueError(f"Field '{field}' is missing or contains no text.")

            extracted_data[field] = match.group(1).strip()

        try:
            return SOAPNote.model_validate(extracted_data)
        except ValidationError as e:
            raise ValueError(f"Data validation failed: {e}")

    async def create_note(self, patient_id: str, file: UploadFile) -> PatientNote:
        file_text = await self.file_conversion_service.convert_to_text(file)
        soap_note = self._get_soap_note(file_text)
        note_data = PatientNoteBaseData(
            patient_id=patient_id,
            assessment=soap_note.a,
            encounter_date=soap_note.encounter_date,
            subjective=soap_note.s,
            objective=soap_note.o,
            physician=soap_note.signed,
            plan=soap_note.p,
        )
        return await self.repository.create_note(note_data)

    async def delete_note(self, note_id: str) -> PatientNote | None:
        return await self.repository.delete_note(note_id)
