from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .enums import IncidentStatus


@dataclass(slots=True)
class Incident:
    incident_id: int
    employee_id: int
    description: Optional[str]
    cost: Optional[float]
    date: Optional[str]
    status: IncidentStatus
    status_addressed: bool
    paid_all: bool
    deleted: bool
