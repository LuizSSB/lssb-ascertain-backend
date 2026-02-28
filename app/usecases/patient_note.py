from datetime import date

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
        def extract_segment(text: str, start_marker: str, end_marker: str | None = None) -> tuple[str, str]:
            start_idx = text.find(start_marker)
            if start_idx == -1:
                raise ValueError(f"Marker '{start_marker}' not found in note.")

            content_start = start_idx + len(start_marker)

            if end_marker:
                end_idx = text.find(end_marker, content_start)
                if end_idx == -1:
                    raise ValueError(f"End marker '{end_marker}' for '{start_marker}' not found.")
                content = text[content_start:end_idx].strip()
                remaining = text[end_idx:]
            else:
                content = text[content_start:].strip()
                remaining = ""

            if not content:
                raise ValueError(f"Field following '{start_marker}' is empty.")

            return content, remaining

        date_label = "Encounter Date:"
        date_start = note.find(date_label)
        if date_start == -1:
            raise ValueError("Encounter Date not found.")
        date_str = note[date_start + len(date_label) :].strip()[:10]

        current_note = note[date_start + len(date_label) + 10 :]
        s_content, current_note = extract_segment(current_note, "S:", "O:")
        o_content, current_note = extract_segment(current_note, "O:", "A:")
        a_content, current_note = extract_segment(current_note, "A:", "P:")
        p_content, current_note = extract_segment(current_note, "P:", "Signed:")
        signed_block, _ = extract_segment(current_note, "Signed:")
        physician_name = signed_block.split("\n")[0].split(",")[0].strip()

        try:
            return SOAPNote(
                encounter_date=date.fromisoformat(date_str),
                s=s_content,
                o=o_content,
                a=a_content,
                p=p_content,
                signed=physician_name,
            )
        except ValidationError as e:
            raise ValueError(f"Validation error: {e}")

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
