from fastapi import APIRouter
from fastapi.responses import Response
from ..services.registry import registry

router = APIRouter(tags=["misc"])

@router.get("/services")
async def list_services():
    return {"services": registry.list()}

@router.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)

@router.get("/_health")
async def health():
    return {"status": "ok"}
