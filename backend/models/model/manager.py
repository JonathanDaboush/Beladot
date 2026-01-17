from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Manager:
    manager_id: int
    user_id: int
    department_id: int
    is_active: bool
    created_at: Optional[datetime]
    last_active_at: Optional[datetime]
