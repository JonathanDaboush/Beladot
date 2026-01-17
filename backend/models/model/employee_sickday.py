from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from .enums import PTOStatus


@dataclass(slots=True)
class EmployeeSickDay:
    sickday_id: int
    emp_id: int
    date: date
    status: PTOStatus
    approved_by_manager_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
