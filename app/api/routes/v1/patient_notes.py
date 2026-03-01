from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.ioc import ioc_container_type
from app.models.api import EntityResponse, ErrorResponse, ListResponse
from app.models.api.patient_notes import GETPatientNotes
from app.models.exceptions import UnsupportedFileType
from app.models.patient_note import PatientNote
from app.usecases.patient_note import PatientNoteUsecases

ROUTER_V1_PATIENT_NOTES = APIRouter(prefix="", tags=["patient-notes"])


PatientNoteUsecasesDependency = Annotated[
    PatientNoteUsecases, Depends(Provide[ioc_container_type().patient_note_usecases])
]


@ROUTER_V1_PATIENT_NOTES.get("/patients/{patient_id}/notes")
@inject
async def get_notes(
    usecase: PatientNoteUsecasesDependency, patient_id: str, request: Annotated[GETPatientNotes, Depends()]
) -> ListResponse[PatientNote]:
    patients, next_token = await usecase.list_notes(
        patient_id,
        limit=request.limit,
        next_token=request.parsed_next_token,
    )
    return ListResponse(next_token=str(next_token) if next_token else None, data=patients)


_MAX_BYTES_NOTE_FILE = 1024 * 1024  # 1mb


@ROUTER_V1_PATIENT_NOTES.post("/patients/{patient_id}/notes", status_code=201)
@inject
async def post_note(
    usecase: PatientNoteUsecasesDependency, patient_id: str, file: Annotated[UploadFile, File(...)]
) -> EntityResponse[PatientNote]:
    if file.size and file.size > _MAX_BYTES_NOTE_FILE:
        raise HTTPException(413, detail=ErrorResponse(message=f"Note file cannot exceed {_MAX_BYTES_NOTE_FILE} bytes"))
    try:
        note = await usecase.create_note(patient_id, file)
        return EntityResponse(data=note)
    except UnsupportedFileType as e:
        raise HTTPException(status_code=400, detail=ErrorResponse(message=str(e)))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=ErrorResponse(message=str(e)))
    finally:
        await file.close()


@ROUTER_V1_PATIENT_NOTES.delete("/patients/notes/{note_id}")
@inject
async def delete_note(usecase: PatientNoteUsecasesDependency, note_id: str) -> EntityResponse[PatientNote]:
    if not (note := await usecase.delete_note(note_id)):
        raise HTTPException(404)

    return EntityResponse(data=note)
