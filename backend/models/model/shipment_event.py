from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .enums import ShipmentEventStatus


@dataclass(slots=True)
class ShipmentEvent:
    event_id: int
    shipment_id: int
    status: ShipmentEventStatus
    description: Optional[str]
    location: Optional[str]
    occurred_at: Optional[datetime]
 
