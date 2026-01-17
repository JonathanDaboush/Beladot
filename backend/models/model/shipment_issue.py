from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class ShipmentIssue:
    issue_id: int
    shipment_id: int
    shipment_employee_name: str
    issue_type: str
    description: Optional[str]
    created_at: Optional[datetime]
    appointted_to: Optional[str]
 