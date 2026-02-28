from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.ioc import ioc_container_type
from app.models.api import EntityResponse, ErrorResponse, ListResponse
from app.models.api.patient_notes import GETPatientNotes
from app.models.patient_note import PatientNote
from app.models.utils import SkipNextToken
from app.usecases.patient_note import PatientNoteUsecases

ROUTER_V1_PATIENT_NOTES = APIRouter(prefix="", tags=["patient-notes"])


PatientNoteUsecasesDependency = Annotated[
    PatientNoteUsecases, Depends(Provide[ioc_container_type().patient_note_usecases])
]


@ROUTER_V1_PATIENT_NOTES.get("/patients/{patient_id}/notes")
@inject
async def get_notes(
    patient_id: str, request: Annotated[GETPatientNotes, Depends()], usecase: PatientNoteUsecasesDependency
) -> ListResponse[PatientNote]:
    try:
        next_token = SkipNextToken.from_string(request.next_token) if request.next_token else None
    except Exception as e:
        raise HTTPException(400, ErrorResponse(message="Invalid next token", cause=e))

    patients, next_token = await usecase.list_notes(
        patient_id,
        limit=request.limit,
        next_token=next_token,
        sort_order=request.sort_order,
    )
    return ListResponse(next_token=str(next_token) if next_token else None, data=patients)


@ROUTER_V1_PATIENT_NOTES.post("/patients/{patient_id}/notes")
async def post_note(
    patient_id: str, usecase: PatientNoteUsecasesDependency, file: Annotated[UploadFile, File(...)]
) -> EntityResponse[PatientNote]:
    if (file.filename and not file.filename.endswith(".txt")) or file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail=ErrorResponse(message="Patient notes must be in txt format"))

    try:
        content_bytes = await file.read()
        content_str = content_bytes.decode("utf-8")
        note = await usecase.create_note(patient_id, content_str)
        return EntityResponse(data=note)
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail=ErrorResponse(message="File content is not valid UTF-8."))
    finally:
        await file.close()


@ROUTER_V1_PATIENT_NOTES.patch("/patients/notes/{note_id}")
@inject
async def delete_note(note_id: str, usecase: PatientNoteUsecasesDependency) -> EntityResponse[PatientNote]:
    if not (note := await usecase.delete_note(note_id)):
        raise HTTPException(404)

    return EntityResponse(data=note)
