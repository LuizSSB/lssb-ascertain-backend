from models.api import ListRequest
from models.patient_note import PatientNoteBaseData
from models.utils import SortOrder


class GETPatientNotes(ListRequest):
    sort_order: SortOrder = "asc"


POSTPatientNote = PatientNoteBaseData
