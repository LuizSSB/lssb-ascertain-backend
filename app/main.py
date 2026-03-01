from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes  # type: ignore
from app.api.routes.v1.patient_notes import ROUTER_V1_PATIENT_NOTES
from app.api.routes.v1.patients import ROUTER_V1_PATIENTS
from app.ioc import ioc_container, ioc_container_type, ioc_setup_root

ioc_setup_root(inject_packages={routes})


@asynccontextmanager
async def _lifespan(app: FastAPI):
    container_type = ioc_container_type()
    container = ioc_container()
    await container_type.lifecycle_setup(container)
    yield


app = FastAPI(lifespan=_lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ROUTER_V1_PATIENTS)
app.include_router(ROUTER_V1_PATIENT_NOTES)
