"""
employee_snapshot.py

Expose the canonical EmployeeSnapshot ORM model from the persistence layer to
avoid duplicate table declarations.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EmployeeSnapshot:
	full_name: str
	department_name: str
	role: str
	approved_by_name: str
