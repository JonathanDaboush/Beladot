from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RefundSnapshot:
	id: str
	payment_user_name: str
	order_number: str
	amount: float
	reason: str
	approved_by_name: str
	status: str
