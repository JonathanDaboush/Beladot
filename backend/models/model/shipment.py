"""
shipment.py

Expose the canonical Shipment ORM model from the persistence layer to avoid
duplicate table declarations. Use backend.persistance.shipment.Shipment as the
single source of truth for the 'shipment' table.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .enums import ShipmentStatus


@dataclass(slots=True)
class Shipment:
	shipment_id: int
	order_id: int
	shipment_status: ShipmentStatus
	shipped_at: Optional[datetime]
	delivered_at: Optional[datetime]
	created_at: Optional[datetime]
	updated_at: Optional[datetime]


