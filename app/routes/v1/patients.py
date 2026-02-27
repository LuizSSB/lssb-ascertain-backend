from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from ioc.container import Container
from models.api import EntityResponse, ErrorResponse, ListResponse
from models.api.patients import GETPatients, PATCHPatient, POSTPatient
from models.patient import Patient
from models.utils import SkipNextToken
from usecases.patient import PatientUsecases

ROUTER_V1_PATIENTS = APIRouter(prefix="/patients", tags=["patients"])

PatientUsecasesDependency = Annotated[PatientUsecases, Depends(Provide[Container.patient_usecases])]


@ROUTER_V1_PATIENTS.get("")
@inject
async def get_patients(
    request: Annotated[GETPatients, Depends()], usecase: PatientUsecasesDependency
) -> ListResponse[Patient]:
    print("usecase", usecase)
    try:
        next_token = SkipNextToken.from_string(request.next_token) if request.next_token else None
    except Exception as e:
        raise HTTPException(400, ErrorResponse(message="Invalid next token", cause=e))

    patients, next_token = await usecase.list_patients(
        search_term=request.search_term,
        limit=request.limit,
        next_token=next_token,
        sort_by=(request.sort_field, request.sort_order) if request.sort_field else None,
    )
    return ListResponse(next_token=str(next_token) if next_token else None, data=patients)


@ROUTER_V1_PATIENTS.get("/{patient_id}")
@inject
async def get_patient(patient_id: str, usecase: PatientUsecasesDependency) -> EntityResponse[Patient]:
    if not (patient := await usecase.get_patient(patient_id)):
        raise HTTPException(404)

    return EntityResponse(data=patient)


@ROUTER_V1_PATIENTS.post("")
@inject
async def create_patient(patient_data: POSTPatient, usecase: PatientUsecasesDependency) -> EntityResponse[Patient]:
    patient = await usecase.create_patient(patient_data)
    return EntityResponse(data=patient)


@ROUTER_V1_PATIENTS.patch("/{patient_id}")
@inject
async def patch_patient(
    patient_id: str, update: PATCHPatient, usecase: PatientUsecasesDependency
) -> EntityResponse[Patient]:
    if not (patient := await usecase.update_patient(patient_id, update)):
        raise HTTPException(404)

    return EntityResponse(data=patient)


@ROUTER_V1_PATIENTS.patch("/{patient_id}")
@inject
async def delete_patient(patient_id: str, usecase: PatientUsecasesDependency) -> EntityResponse[Patient]:
    if not (patient := await usecase.delete_patient(patient_id)):
        raise HTTPException(404)

    return EntityResponse(data=patient)
