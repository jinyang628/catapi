from pydantic import BaseModel


class Student(BaseModel):
    id: int
    name: str
    teacher_id: int


class StudentDetail(BaseModel):
    name: str
    teacher_name: str
    cumulative_gpa: float


class GetStudentDetailsResponse(BaseModel):
    details: list[StudentDetail]


class GpaDetail(BaseModel):
    name: str
    cumulative_gpa: float


class GetGpaDetailsResponse(BaseModel):
    details: list[GpaDetail]
