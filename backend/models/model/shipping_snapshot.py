from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

from .enums import ShippingSnapshotStatus


@dataclass(slots=True)
class ShippingSnapshot:
    snapshot_id: int
    shipment_id: int
    status: ShippingSnapshotStatus
    events: List[Dict] = field(default_factory=list)
    items: List[Dict] = field(default_factory=list)
    total_cost: float = 0.0
    created_at: Optional[datetime] = None
