from models.api import ListRequest
from models.patient import Patient, PatientBaseData, PatientUpdateData
from models.utils import SortOrder


class GETPatients(ListRequest):
    sort_field: Patient.SortField | None = None
    sort_order: SortOrder = "asc"
    search_term: str | None = None


POSTPatient = PatientBaseData


PATCHPatient = PatientUpdateData
