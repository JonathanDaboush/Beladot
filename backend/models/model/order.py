from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Order:
	order_id: int
	user_id: int
	cart_id: Optional[int]
	order_status: str
	total_amount: float
	created_at: Optional[datetime]
	updated_at: Optional[datetime]
	order_number: int
