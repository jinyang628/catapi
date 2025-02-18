from app.models.students import (
    GetGpaDetailsResponse,
    GetStudentDetailsResponse,
    GpaDetail,
    Student,
    StudentDetail,
)
from app.utils.boolean_clause import BooleanClause, Operator
from app.utils.database import DatabaseClient
from app.utils.gpa import calculate_cumulative_gpa


class StudentsService:
    async def modify_teacher(self, student_id: int, teacher_id: int) -> Student:
        client = await DatabaseClient.get_instance()
        results: list = await client.patch(
            table_name="students",
            data={"teacher_id": teacher_id},
            boolean_clause=BooleanClause(column_name="id", operator=Operator.EQ, value=student_id),
        )
        students: list[Student] = [Student.model_validate(result) for result in results]
        if len(students) != 1:
            raise ValueError(
                "More than one student found while trying to modify teacher assignment"
            )
        return students[0]

    async def get_student_details(self) -> GetStudentDetailsResponse:
        client = await DatabaseClient.get_instance()
        results: list = await client.get(
            table_name="students",
            column_names=["name", "teachers(name)", "grades(grade)"],  # inner join
        )
        details: list[StudentDetail] = []
        for result in results:
            grade_list: list = [grade["grade"] for grade in result["grades"]]
            details.append(
                StudentDetail(
                    name=result["name"],
                    teacher_name=result["teachers"]["name"],
                    cumulative_gpa=calculate_cumulative_gpa(grade_list=grade_list),
                )
            )

        return GetStudentDetailsResponse(details=details)

    async def get_gpa_details(
        self, start_semester: int, end_semester: int
    ) -> GetGpaDetailsResponse:
        """
        The following RPC is created in Supabase:

        CREATE OR REPLACE FUNCTION get_students_with_filtered_grades(
            start_semester INT,
            end_semester INT
        )
        RETURNS TABLE (
            name TEXT,
            filtered_grades JSONB
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT
                s.name,
                jsonb_agg(
                    jsonb_build_object(
                        'grade', g.grade,
                        'semester', g.semester
                    )
                ) AS filtered_grades
            FROM
                students s
            JOIN
                grades g ON s.id = g.student_id
            WHERE
                g.semester BETWEEN start_semester AND end_semester
            GROUP BY
                s.name;
        END;
        $$ LANGUAGE plpgsql;
        """
        client = await DatabaseClient.get_instance()
        results: list = await client.execute_rpc(
            "get_students_with_filtered_grades",
            params={
                "start_semester": start_semester,
                "end_semester": end_semester,
            },
        )

        details: list[GpaDetail] = []
        for result in results:
            grade_list: list = [grade["grade"] for grade in result["filtered_grades"]]
            details.append(
                GpaDetail(
                    name=result["name"],
                    cumulative_gpa=calculate_cumulative_gpa(grade_list=grade_list),
                )
            )
        return GetGpaDetailsResponse(details=details)
