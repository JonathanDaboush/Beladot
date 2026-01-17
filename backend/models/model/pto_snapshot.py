"""
pto_snapshot.py

Expose the canonical PTOSnapshot ORM model from the persistence layer to
avoid duplicate table declarations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class PTOSnapshot:
	employee_name: str
	incident_number: int
	pto_days: int
	created_at: Optional[datetime]
