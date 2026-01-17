"""
payment_snapshot.py

Expose the canonical PaymentSnapshot ORM model from the persistence layer to
avoid duplicate table declarations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class PaymentSnapshot:
	id: str
	user_full_name: str
	order_number: str
	amount: float
	currency: str
	payment_method: str
	last4_digits: str
	status: str
	approved_by_name: str
	date_of_creation: Optional[datetime]
