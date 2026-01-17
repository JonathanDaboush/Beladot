"""
address_snapshot.py

Expose the canonical AddressSnapshot ORM model from the persistence layer to
avoid duplicate table declarations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class AddressSnapshot:
	reference_type: str
	recipient_name: str
	street_line_1: str
	street_line_2: str
	city: str
	state_province: str
	postal_code: str
	country: str
	phone_number: str
	order_number: Optional[str]
	shipment_id: Optional[str]
