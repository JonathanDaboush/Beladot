from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EmployeeComponent:
	id: int
	img_url: str
	description: str
	department_id: int
