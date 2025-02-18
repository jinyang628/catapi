import math

from app.models.grades import GradeValue


def calculate_cumulative_gpa(grade_list: list[GradeValue]) -> float:
    """Calculates the cumulative GPA for a list of grades, rounded to two decimal places."""
    total_gpa = 0
    for grade in grade_list:
        match grade:
            case GradeValue.A_PLUS:
                total_gpa += 4.0
            case GradeValue.A:
                total_gpa += 4.0
            case GradeValue.A_MINUS:
                total_gpa += 3.7
            case GradeValue.B_PLUS:
                total_gpa += 3.3
            case GradeValue.B:
                total_gpa += 3.0
            case GradeValue.B_MINUS:
                total_gpa += 2.7
            case GradeValue.C_PLUS:
                total_gpa += 2.3
            case GradeValue.C:
                total_gpa += 2.0
            case GradeValue.C_MINUS:
                total_gpa += 1.7
            case GradeValue.D_PLUS:
                total_gpa += 1.3
            case GradeValue.D:
                total_gpa += 1.0
            case GradeValue.E:
                total_gpa += 0.0
            case GradeValue.F:
                total_gpa += 0.0
            case _:
                raise ValueError(f"Invalid grade: {grade}")

    return round(total_gpa / len(grade_list), 2)
