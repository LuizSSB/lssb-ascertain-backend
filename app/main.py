import routes
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from ioc.container import Container
from routes.v1.patients import ROUTER_V1_PATIENTS
from utils.modules import get_module_filepaths

container = Container()
container.wire(modules=get_module_filepaths(routes))


@asynccontextmanager
async def _lifespan(app: FastAPI):
    await container.db().create_database()
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
