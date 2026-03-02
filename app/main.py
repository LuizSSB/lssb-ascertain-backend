from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import routes
from app.api.middleware.logging import LoggingMiddleware
from app.api.routes import ROUTER_ROOT
from app.api.routes.auth import ROUTER_AUTH
from app.api.routes.v1.patient_notes import ROUTER_V1_PATIENT_NOTES
from app.api.routes.v1.patients import ROUTER_V1_PATIENTS
from app.models.api import ErrorResponse
from app.tooling.ioc import ioc_container, ioc_container_type, ioc_setup_root

ioc_setup_root(inject_packages={routes})


@asynccontextmanager
async def _lifespan(app: FastAPI):
    container_type = ioc_container_type()
    container = ioc_container()
    await container_type.lifecycle_setup(container)
    yield


app = FastAPI(lifespan=_lifespan)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=500, content=ErrorResponse(message=str(exc)))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content=exc.detail, headers=exc.headers)

    logger = ioc_container_type().logger("global_exception_handler")
    logger.error("failed to process request", error=str(exc))

    return JSONResponse(status_code=500, content=ErrorResponse(message=str(exc)))


app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ROUTER_ROOT)
app.include_router(ROUTER_AUTH)
app.include_router(ROUTER_V1_PATIENTS)
app.include_router(ROUTER_V1_PATIENT_NOTES)
