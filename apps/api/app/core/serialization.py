from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlalchemy.inspection import inspect


def json_value(value):
    if isinstance(value, (UUID, datetime, date, Decimal)):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    return value


def model_dict(instance) -> dict:
    mapper = inspect(instance).mapper
    return {
        column.key: json_value(getattr(instance, column.key))
        for column in mapper.column_attrs
    }
