"""
paystub_snapshot.py

Expose the canonical PaystubSnapshot ORM model from the persistence layer to
avoid duplicate table declarations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class PaystubSnapshot:
	employee_name: str
	incident_number: int
	hours_worked: float
	sick_days: int
	pto_days: int
	hourly_rate: float
	gross_pay: float
	deductions: float
	net_pay: float
	created_at: Optional[datetime]
