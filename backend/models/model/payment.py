
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Payment:
	payment_id: int
	order_id: int
	user_id: int
	amount: float
	currency: str
	status: str
	created_at: Optional[datetime]
	updated_at: Optional[datetime]
