from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from app.ioc import ioc_container_type
from app.models.ai.summary import SummaryAudience, SummaryLength
from app.models.api import EntityResponse, ErrorResponse, ListResponse
from app.models.api.patients import GETPatients, PATCHPatient, POSTPatient
from app.models.exceptions import NotFoundException
from app.models.patient import Patient
from app.models.patient_summary import PatientSummary
from app.models.utils import SkipNextToken
from app.usecases.patient import PatientUsecases
from app.usecases.patient_summary import PatientSummaryUsecases

ROUTER_V1_PATIENTS = APIRouter(prefix="/patients", tags=["patients"])

PatientUsecasesDependency = Annotated[PatientUsecases, Depends(Provide[ioc_container_type().patient_usecases])]


@ROUTER_V1_PATIENTS.get("")
@inject
async def get_patients(
    usecase: PatientUsecasesDependency, request: Annotated[GETPatients, Depends()]
) -> ListResponse[Patient]:
    try:
        next_token = SkipNextToken.from_string(request.next_token) if request.next_token else None
    except Exception as e:
        raise HTTPException(400, ErrorResponse(message="Invalid next token", cause=str(e)))

    patients, next_token = await usecase.list_patients(
        search_term=request.search_term,
        limit=request.limit,
        next_token=next_token,
        sort_by=(request.sort_field, request.sort_order) if request.sort_field else None,
    )
    return ListResponse(next_token=str(next_token) if next_token else None, data=patients)


@ROUTER_V1_PATIENTS.get("/{patient_id}")
@inject
async def get_patient(usecase: PatientUsecasesDependency, patient_id: str) -> EntityResponse[Patient]:
    if not (patient := await usecase.get_patient(patient_id)):
        raise HTTPException(404)

    return EntityResponse(data=patient)


@ROUTER_V1_PATIENTS.post("", status_code=201)
@inject
async def create_patient(usecase: PatientUsecasesDependency, patient_data: POSTPatient) -> EntityResponse[Patient]:
    patient = await usecase.create_patient(patient_data)
    return EntityResponse(data=patient)


@ROUTER_V1_PATIENTS.patch("/{patient_id}")
@inject
async def patch_patient(
    usecase: PatientUsecasesDependency, patient_id: str, update: PATCHPatient
) -> EntityResponse[Patient]:
    if not (patient := await usecase.update_patient(patient_id, update)):
        raise HTTPException(404)

    return EntityResponse(data=patient)


@ROUTER_V1_PATIENTS.delete("/{patient_id}")
@inject
async def delete_patient(usecase: PatientUsecasesDependency, patient_id: str) -> EntityResponse[Patient]:
    if not (patient := await usecase.delete_patient(patient_id)):
        raise HTTPException(404)

    return EntityResponse(data=patient)


@ROUTER_V1_PATIENTS.get("/{patient_id}/summary")
@inject
async def summarize_patient(
    usecase: Annotated[PatientSummaryUsecases, Depends(Provide[ioc_container_type().patient_summary_usecases])],
    patient_id: str,
    length: SummaryLength = SummaryLength.SHORT,
    audience: SummaryAudience = SummaryAudience.LAYPEOPLE,
) -> EntityResponse[PatientSummary]:
    try:
        data = await usecase.summarize(patient_id, length=length, audience=audience)
        return EntityResponse(data=data)
    except NotFoundException:
        raise HTTPException(404)
