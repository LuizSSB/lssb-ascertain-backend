from app.models.api import ListRequest
from app.models.patient_note import PatientNoteBaseData
from app.models.utils import SortOrder


class GETPatientNotes(ListRequest):
    sort_order: SortOrder = "asc"


POSTPatientNote = PatientNoteBaseData
