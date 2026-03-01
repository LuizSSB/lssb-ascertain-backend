from datetime import date
from typing import Any, cast

import pytest
from langchain_core.language_models.chat_models import BaseChatModel

from app.models.patient import Patient
from app.models.patient_note import PatientNote
from app.models.summary import SummaryAudience, SummaryLength
from app.services.summarization.deepagents import DeepAgentsSummarizationService
from app.tooling.logging import AppLogger


def _make_dummy_agent(response_text: str):
    class DummyMessage:
        def __init__(self, content: str):
            self.content = content

    class DummyAgent:
        def __init__(self, resp: str):
            self._resp = resp

        def invoke(self, payload: Any):
            return {"messages": [DummyMessage("ignored"), DummyMessage(self._resp)]}

    return DummyAgent(response_text)


def test_deep_agents_summarization_service_empty_notes_returns_message(logger: AppLogger) -> None:
    svc = DeepAgentsSummarizationService(model=cast(Any, None), logger=logger)

    patient = Patient(id="p1", name="Test Patient", birthdate=date(1990, 1, 1))

    result = svc.summarize_patient(patient, notes=[], audience=SummaryAudience.CLINICIANS, length=SummaryLength.SHORT)
    assert result == "No clinical notes available to generate a summary."


def test_deep_agents_summarization_service_invokes_agent_and_returns_summary(
    logger: AppLogger, monkeypatch: pytest.MonkeyPatch
) -> None:
    dummy_response = "This is a generated summary."

    def _fake_create_deep_agent(model: BaseChatModel | None, system_prompt: str):
        return _make_dummy_agent(dummy_response)

    monkeypatch.setattr("app.services.summarization.deepagents.create_deep_agent", _fake_create_deep_agent)

    svc = DeepAgentsSummarizationService(model=cast(Any, None), logger=logger)

    patient = Patient(id="p1", name="Test Patient", birthdate=date(1990, 1, 1))
    note = PatientNote(
        id="n1",
        patient_id="p1",
        encounter_date=date(2024, 6, 1),
        subjective="Subj",
        objective="Obj",
        assessment="Assess",
        plan="Plan",
        physician="Dr",
    )

    result = svc.summarize_patient(
        patient, notes=[note], audience=SummaryAudience.LAYPEOPLE, length=SummaryLength.SHORT
    )
    assert result == dummy_response
