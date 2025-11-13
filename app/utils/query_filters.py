from __future__ import annotations

import math
from typing import Iterable, Optional

from sqlalchemy import Select, and_, func
from sqlalchemy.orm import InstrumentedAttribute


def apply_sort(stmt: Select, model, sort_expression: Optional[str]) -> Select:
    if not sort_expression:
        return stmt

    sort_fields = [field.strip() for field in sort_expression.split(",") if field.strip()]
    for field in sort_fields:
        desc = field.startswith("-")
        attr_name = field[1:] if desc else field
        attr = getattr(model, attr_name, None)
        if attr is None or not isinstance(attr, InstrumentedAttribute):
            continue
        stmt = stmt.order_by(attr.desc() if desc else attr.asc())
    return stmt


def add_range_filter(
    stmt: Select,
    value,
    attr: InstrumentedAttribute,
    *,
    comparator,
):
    if value is None:
        return stmt
    return stmt.where(comparator(attr, value))


def haversine_distance_expr(lat1, lon1, lat2_field, lon2_field):
    """Return expression calculating distance in km."""
    return (
        6371
        * func.acos(
            func.cos(func.radians(lat1))
            * func.cos(func.radians(lat2_field))
            * func.cos(func.radians(lon2_field) - func.radians(lon1))
            + func.sin(func.radians(lat1)) * func.sin(func.radians(lat2_field))
        )
    )
