from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SellerExpense:
	id: int
	order_id: int
	amount: float
