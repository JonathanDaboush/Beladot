
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Employee:
	emp_id: int
	user_id: int
	department_id: int
	notes: Optional[str]
