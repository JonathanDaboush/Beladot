from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Shift:
    shift_id: int
    department_id: int
    assigned_emp_id: int
    start_time: datetime
    end_time: datetime
    created_by_manager_id: int
    status: str
