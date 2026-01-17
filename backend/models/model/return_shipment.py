from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class ReturnShipment:
    return_shipment_id: int
    original_shipment_id: int
    return_status: str
    shipped_at: Optional[datetime]
    received_at: Optional[datetime]
"""
return_shipment.py

Model for return shipment entity.
Represents a shipment returned by a customer, including status and timestamps.
"""
 
