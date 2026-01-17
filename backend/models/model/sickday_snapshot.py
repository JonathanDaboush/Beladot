from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class SickDaySnapshot:
    employee_name: str
    sick_days: int
    created_at: Optional[datetime]
