from deepagents import create_deep_agent  # type: ignore
from langchain_core.language_models.chat_models import BaseChatModel

from app.models.ai.summary import SummaryAudience, SummaryLength
from app.models.patient import Patient
from app.models.patient_note import PatientNote
from app.services.summarization import SummarizationService


class DeepAgentsSummarizationService(SummarizationService):
    def __init__(self, model: BaseChatModel):
        self.model = model

    def summarize_patient(
        self,
        patient: Patient,
        *,
        notes: list[PatientNote],
        audience: SummaryAudience,
        length: SummaryLength,
    ) -> str:
        if not notes:
            return "No clinical notes available to generate a summary."

        # Build structured clinical context
        notes_block = "\n\n".join(
            f"""
## Encounter Date: {note.encounter_date}
Physician: {note.physician}

Subjective:
{note.subjective}

Objective:
{note.objective}

Assessment:
{note.assessment}

Plan:
{note.plan}
    """.strip()
            for note in sorted(notes, key=lambda n: n.encounter_date)
        )

        match audience:
            case SummaryAudience.CLINICIANS:
                audience_instruction = """
Use clinical terminology. Be precise and structured, but maintain narrative coherence. Highlight diagnoses, differential diagnoses, medications, treatment plans, and clinically relevant objective findings.
""".strip()
            case SummaryAudience.LAYPEOPLE:
                audience_instruction = """
Use plain, non-technical language. Explain medical terms when necessary. Focus on clarity and patient understanding.
""".strip()

        match length:
            case SummaryLength.SHORT:
                length_instruction = """
Keep the summary concise (approximately 150–250 words). Prioritize the most important clinical information.
""".strip()
            case SummaryLength.VERBOSE:
                length_instruction = """
Provide a comprehensive summary (approximately 400–700 words). Include relevant clinical evolution, treatments, and reasoning.
""".strip()

        system_prompt = """
You are a clinical documentation assistant. Your task is to generate a coherent, human-readable patient summary based strictly on the provided information. Do not invent information that is not present in the notes.
""".strip()

        user_prompt = f"""
# Patient Profile
Name: {patient.name}
Birthdate: {patient.birthdate}

# Clinical Notes:
{notes_block}

# Instructions:
- Produce a coherent narrative summary.
- Clearly communicate key diagnoses, medications, treatments, and observations.
- Avoid bullet points unless necessary for clarity.
- Ensure chronological flow.
- The patient's date of birth will be later included in the summary's header, so no need to state it.
- {audience_instruction}
- {length_instruction}
""".strip()

        result = create_deep_agent(
            model=self.model,
            system_prompt=system_prompt,
        ).invoke(  # type: ignore
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ]
            },
        )

        return result["messages"][-1].content
