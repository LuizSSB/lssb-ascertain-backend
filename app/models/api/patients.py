from app.models.api import ListRequest
from app.models.patient import Patient, PatientBaseData, PatientNextToken, PatientUpdateData
from app.models.utils import SortOrder


class GETPatients(ListRequest):
    sort_field: Patient.SortField | None = None
    sort_order: SortOrder | None = None
    search_term: str | None = None

    @property
    def parsed_next_token(self) -> PatientNextToken | None:

        if (self.sort_field or self.sort_order or self.search_term) and self.next_token:
            raise ValueError("Request should have either next_token or the filtering/sorting fields, not both")

        if self.next_token:
            return PatientNextToken.model_validate_json(self.next_token)

        if self.sort_field or self.sort_order or self.search_term:
            return PatientNextToken(
                skip=0,
                sort_field=self.sort_field,
                sort_order=self.sort_order,
                search_term=self.search_term,
            )

        return None


POSTPatient = PatientBaseData


PATCHPatient = PatientUpdateData
