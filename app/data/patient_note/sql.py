from contextlib import AbstractAsyncContextManager
from typing import Callable, Iterable

from data.patient_note import PatientNoteRepository
from models.patient_note import PatientNote, PatientNoteBaseData
from models.sql.patient_note import SQLPatientNote
from models.utils import SortOrder
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession


class SQLPatientNoteRepository(PatientNoteRepository):

    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]) -> None:
        self.session_factory = session_factory

    async def list_notes(
        self, patient_id: str, *, sort_order: SortOrder | None = None, skip: int | None = None, limit: int | None = None
    ) -> Iterable[PatientNote]:
        query = select(SQLPatientNote).filter(SQLPatientNote.patient_id == patient_id)
        if skip:
            query = query.offset(skip)
        if limit:
            query = query.limit(limit)
        if sort_order:
            match sort_order:
                case "asc":
                    order_function = asc
                case "desc":
                    order_function = desc

            query.order_by(order_function(SQLPatientNote.encounter_date))

        async with self.session_factory() as session:
            results = (await session.execute(query)).scalars().all()
            return (r.as_common_type for r in results)

    async def create_note(self, note_data: PatientNoteBaseData) -> PatientNote:
        async with self.session_factory() as session:
            note = SQLPatientNote(
                patient_id=note_data.patient_id,
                encounter_date=note_data.encounter_date,
                subjective=note_data.subjective,
                objective=note_data.objective,
                assessment=note_data.assessment,
                plan=note_data.plan,
            )
            session.add(note)
            await session.commit()
            await session.refresh(note)
            return note.as_common_type

    async def delete_note(self, note_id: str) -> PatientNote | None:
        async with self.session_factory() as session:
            if not (
                note := (
                    await session.execute(select(SQLPatientNote).filter(SQLPatientNote.id == note_id))
                ).scalar_one_or_none()
            ):
                return None

            await session.delete(note)
            await session.commit()
            return note.as_common_type
