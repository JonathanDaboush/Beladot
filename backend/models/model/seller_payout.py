from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(slots=True)
class SellerPayout:
    payout_id: int
    seller_id: int
    amount: float
    currency: str
    date_of_payment: date
    status: str
    created_at: Optional[datetime]
 
