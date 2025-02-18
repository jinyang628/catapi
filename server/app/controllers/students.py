import logging

from fastapi import APIRouter, HTTPException
from httpx import codes

from app.models.students import GetGpaDetailsResponse, GetStudentDetailsResponse, Student
from app.services.students import StudentsService

log = logging.getLogger(__name__)


class StudentsController:
    def __init__(self, service: StudentsService):
        self.router = APIRouter()
        self.service = service
        self.setup_routes()

    def setup_routes(self):
        router = self.router

        @router.get(
            "/details",
            response_model=GetStudentDetailsResponse,
        )
        async def get_student_details() -> GetStudentDetailsResponse:
            try:
                log.info("Getting student details...")
                response: GetStudentDetailsResponse = await self.service.get_student_details()
                log.info("Student details retrieved %s", response.model_dump())
                return response
            except Exception as e:
                log.error("Unexpected error occurred when getting student details: %s", str(e))
                raise HTTPException(
                    status_code=codes.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
                ) from e

        @router.patch(
            "/{student_id}/teacher/{teacher_id}",
            response_model=Student,
        )
        async def modify_teacher(student_id: int, teacher_id: int) -> Student:
            try:
                log.info("Modifying teacher for student %s...", student_id)
                response: Student = await self.service.modify_teacher(
                    student_id=student_id, teacher_id=teacher_id
                )
                log.info("Updated student record %s", response.model_dump())
                return response
            except Exception as e:
                log.error("Unexpected error occurred when modifying teacher %s", str(e))
                raise HTTPException(
                    status_code=codes.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
                ) from e

        @router.get(
            "/gpa",
            response_model=GetGpaDetailsResponse,
        )
        async def get_gpa_details(start_semester: int, end_semester: int) -> GetGpaDetailsResponse:
            try:
                log.info("Getting GPA details...")
                response: GetGpaDetailsResponse = await self.service.get_gpa_details(
                    start_semester=start_semester, end_semester=end_semester
                )
                log.info("GPA details retrieved %s", response.model_dump())
                return response
            except Exception as e:
                log.error("Unexpected error occurred when getting GPA details: %s", str(e))
                raise HTTPException(
                    status_code=codes.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
                ) from e
