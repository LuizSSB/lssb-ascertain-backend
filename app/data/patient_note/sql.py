from typing import Iterable

from sqlmodel import asc, desc, select

from app.data.patient_note import PatientNoteRepository
from app.data.sqldatabase import AsyncSessionFactory
from app.models.patient_note import PatientNote, PatientNoteBaseData
from app.models.sql.patient_note import SQLPatientNote
from app.models.utils import SortOrder
from app.tooling.logging import AppLogger


class SQLPatientNoteRepository(PatientNoteRepository):

    def __init__(self, session_factory: AsyncSessionFactory, logger: AppLogger) -> None:
        self.session_factory = session_factory
        self.logger = logger

    async def list_notes(
        self, patient_id: str, *, sort_order: SortOrder | None = None, skip: int | None = None, limit: int | None = None
    ) -> Iterable[PatientNote]:
        self.logger.debug("list_notes called", patient_id=patient_id, sort_order=sort_order, skip=skip, limit=limit)
        query = select(SQLPatientNote).where(SQLPatientNote.patient_id == patient_id)
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

            query = query.order_by(order_function(SQLPatientNote.encounter_date))

        async with self.session_factory() as session:
            results = (await session.execute(query)).scalars().all()
            self.logger.debug(
                "list_notes returned",
                patient_id=patient_id,
                sort_order=sort_order,
                skip=skip,
                limit=limit,
                count=len(results),
            )
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
                physician=note_data.physician,
            )
            session.add(note)
            await session.commit()
            await session.refresh(note)
            created = note.as_common_type
            self.logger.info("create_note succeeded", patient_id=note_data.patient_id, note_id=created.id)
            return created

    async def delete_note(self, note_id: str) -> PatientNote | None:
        async with self.session_factory() as session:
            if not (
                note := (
                    await session.execute(select(SQLPatientNote).where(SQLPatientNote.id == note_id))
                ).scalar_one_or_none()
            ):
                self.logger.warning("delete_note failed; not found", note_id=note_id)
                return None

            await session.delete(note)
            await session.commit()
            deleted = note.as_common_type
            self.logger.info("delete_note succeeded", patient_id=deleted.patient_id, note_id=deleted.id)
            return deleted
