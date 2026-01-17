from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Refund:
    refund_id: int
    payment_id: int
    order_item_id: Optional[int]
    amount: float
    reason: str
    approved_by_cs_id: Optional[int]
    status: str
    created_at: Optional[datetime]
    processed_at: Optional[datetime]
