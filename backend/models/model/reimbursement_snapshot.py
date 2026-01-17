from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class ReimbursementSnapshot:
    employee_name: str
    incident_number: int
    amount: float
    description: str
    created_at: Optional[datetime]
