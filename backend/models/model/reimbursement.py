from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Reimbursement:
    reimbursement_id: int
    incident_id: int
    description: Optional[str]
    response: Optional[str]
    amount_approved: Optional[float]
    status: bool
    status_addressed: bool
    paid_all: bool
    deleted: bool
