from fastapi import APIRouter

from app.schemas.designers import DesignerWorkload
from app.services.designers import designer_service

router = APIRouter(prefix="/api/designers", tags=["designers"])


@router.get("/workload", response_model=DesignerWorkload)
def get_workload() -> dict:
    return designer_service.get_workload()
