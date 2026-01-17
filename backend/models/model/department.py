"""
Department (domain model)

Pure domain representation of a business department.
This model is intentionally decoupled from the ORM layer
located under backend/persistance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass(slots=True)
class Department:
    department_id: int
    name: str
