import logging

from fastapi import APIRouter

from app.controllers.students import StudentsController
from app.services.students import StudentsService

log = logging.getLogger(__name__)

router = APIRouter()

### Health check


@router.get("/status")
async def status():
    log.info("Status endpoint called")
    return {"status": "ok"}


### Students


def get_students_controller_router():
    service = StudentsService()
    return StudentsController(service=service).router


router.include_router(
    get_students_controller_router(),
    tags=["students"],
    prefix="/api/students",
)
