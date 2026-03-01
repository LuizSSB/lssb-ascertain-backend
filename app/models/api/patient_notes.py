from app.models.api import ListRequest
from app.models.patient_note import PatientNoteBaseData, PatientNoteNextToken
from app.models.utils import SortOrder


class GETPatientNotes(ListRequest):
    sort_order: SortOrder | None = None

    @property
    def parsed_next_token(self) -> PatientNoteNextToken | None:
        if self.sort_order and self.next_token:
            raise ValueError("Request should have either next_token or sort_order, not both")

        if self.next_token:
            return PatientNoteNextToken.model_validate_json(self.next_token)

        if self.sort_order:
            return PatientNoteNextToken(skip=0, sort_order=self.sort_order)

        return None


POSTPatientNote = PatientNoteBaseData
