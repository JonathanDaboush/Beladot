from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .enums import ShipmentItemStatus


@dataclass(slots=True)
class ShipmentItem:
    shipment_item_id: int
    shipment_id: int
    product_id: int
    variant_id: Optional[int]
    shipment_event_id: Optional[int]
    quantity: int
    status: ShipmentItemStatus
