from fastapi import APIRouter

ROUTER_ROOT = APIRouter(prefix="", tags=["root"])


@ROUTER_ROOT.get("/health")
def get_health():
    return
