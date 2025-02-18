from enum import StrEnum
from typing import Any, Optional

from pydantic import BaseModel


class Operator(StrEnum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    LIKE = "like"
    IN = "in"
    NOT_IN = "not_in"


class LogicalOperator(StrEnum):
    AND = "AND"
    OR = "OR"


class BooleanClause(BaseModel):
    column_name: Optional[str] = None  # Optional for non-leaf nodes
    operator: Optional[Operator] = None  # Optional for non-leaf nodes
    value: Optional[Any] = None  # Optional for non-leaf nodes
    logical_operator: Optional[LogicalOperator] = None  # For AND/OR conditions
    left: Optional["BooleanClause"] = None
    right: Optional["BooleanClause"] = None


def apply_boolean_clause(query, boolean_clause: Optional[BooleanClause]):
    """
    Applies the BooleanClause to a Supabase query.
    """
    if not boolean_clause:
        return query

    _apply_boolean_clause_recursive(query, boolean_clause)

    return query


def _apply_boolean_clause_recursive(query, boolean_clause: BooleanClause):
    """
    Recursively applies the BooleanClause to the Supabase query, modifying it in-place.
    """
    # If this is a leaf node (no left/right children), apply the condition directly
    if boolean_clause.column_name and boolean_clause.operator and boolean_clause.value:
        column = boolean_clause.column_name
        operator = boolean_clause.operator
        value = boolean_clause.value

        match operator:
            case Operator.EQ:
                query.eq(column, value)
            case Operator.NEQ:
                query.neq(column, value)
            case Operator.GT:
                query.gt(column, value)
            case Operator.LT:
                query.lt(column, value)
            case Operator.GTE:
                query.gte(column, value)
            case Operator.LTE:
                query.lte(column, value)
            case Operator.LIKE:
                query.like(column, f"%{value}%")
            case Operator.IN:
                query.in_(column, value)
            case Operator.NOT_IN:
                query.not_in(column, value)
            case _:
                raise ValueError(f"Invalid operator: {operator}")

    # If this is a non-leaf node (has left/right children), apply the logical operator
    if boolean_clause.left and boolean_clause.right and boolean_clause.logical_operator:
        match boolean_clause.logical_operator:
            case LogicalOperator.AND:
                query = query.and_(_apply_boolean_clause_recursive(query, boolean_clause.left))
                query = query.and_(_apply_boolean_clause_recursive(query, boolean_clause.right))
            case LogicalOperator.OR:
                query = query.or_(_apply_boolean_clause_recursive(query, boolean_clause.left))
                query = query.or_(_apply_boolean_clause_recursive(query, boolean_clause.right))

    return query
