from datetime import date
from typing import Iterable, List

import pytest

from app.data.patient import PatientRepository
from app.data.patient_note import PatientNoteRepository
from app.models.exceptions import NotFoundException
from app.models.patient import Patient, PatientBaseData, PatientUpdateData
from app.models.patient_note import PatientNote, PatientNoteBaseData
from app.models.summary import SummaryAudience, SummaryLength
from app.models.utils import SortFieldData, SortOrder
from app.services.summarization import SummarizationService
from app.tooling.logging import AppLogger
from app.usecases.patient_summary import PatientSummaryUsecases


class DummyPatientRepo(PatientRepository):
    def __init__(self, patient: Patient | None) -> None:
        self._patient = patient

    async def list_patients(
        self,
        *,
        name: str | None = None,
        sort_by: SortFieldData[Patient.SortField] | None = None,
        skip: int | None = None,
        limit: int | None = None
    ) -> Iterable[Patient]:
        raise NotImplementedError()

    async def get_patient(self, patient_id: str) -> Patient | None:
        return self._patient

    async def create_patient(self, patient_data: PatientBaseData) -> Patient:
        raise NotImplementedError()

    async def update_patient(self, patient_id: str, patient_data: PatientUpdateData) -> Patient | None:
        raise NotImplementedError()

    async def delete_patient(self, patient_id: str) -> Patient | None:
        raise NotImplementedError()


class DummyNoteRepo(PatientNoteRepository):
    def __init__(self, notes: List[PatientNote]) -> None:
        self._notes = notes

    async def list_notes(
        self, patient_id: str, *, sort_order: SortOrder | None = None, skip: int | None = None, limit: int | None = None
    ) -> Iterable[PatientNote]:
        return (n for n in self._notes)

    async def create_note(self, note_data: PatientNoteBaseData) -> PatientNote:
        raise NotImplementedError()

    async def delete_note(self, note_id: str) -> PatientNote | None:
        raise NotImplementedError()


class DummySummarizationService(SummarizationService):
    def __init__(self, out: str) -> None:
        self._out = out

    def summarize_patient(
        self, patient: Patient, *, notes: list[PatientNote], audience: SummaryAudience, length: SummaryLength
    ) -> str:
        return self._out


@pytest.mark.asyncio
async def test_patient_summary_usecases_summarize_returns_summary(logger: AppLogger) -> None:
    patient = Patient(id="p1", name="John", birthdate=date(1990, 1, 1))
    notes = [
        PatientNote(
            id="n1",
            patient_id="p1",
            encounter_date=date(2024, 1, 1),
            subjective="s",
            objective="o",
            assessment="a",
            plan="p",
            physician="dr",
        )
    ]

    patient_repo = DummyPatientRepo(patient)
    note_repo = DummyNoteRepo(notes)
    summarizer = DummySummarizationService("SUMMARY TEXT")

    usecase = PatientSummaryUsecases(patient_repo, note_repo, summarizer, logger)
    result = await usecase.summarize("p1", audience=SummaryAudience.CLINICIANS, length=SummaryLength.SHORT)

    assert "Patient:" in result.header
    assert result.summary == "SUMMARY TEXT"


@pytest.mark.asyncio
async def test_patient_summary_usecases_summarize_missing_patient_raises(logger: AppLogger) -> None:
    patient_repo = DummyPatientRepo(None)
    note_repo = DummyNoteRepo([])
    summarizer = DummySummarizationService("irrelevant")

    usecase = PatientSummaryUsecases(patient_repo, note_repo, summarizer, logger)

    with pytest.raises(NotFoundException):
        await usecase.summarize("missing", audience=SummaryAudience.CLINICIANS, length=SummaryLength.SHORT)
        await usecase.summarize("missing", audience=SummaryAudience.CLINICIANS, length=SummaryLength.SHORT)
