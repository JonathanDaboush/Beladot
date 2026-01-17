from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .enums import RefundRequestStatus


@dataclass(slots=True)
class RefundRequest:
    refund_request_id: int
    order_id: int
    order_item_ids: List[int]
    reason: str
    status: RefundRequestStatus
    date_of_request: Optional[datetime] = None
    description: Optional[str] = None
