from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class FinanceEmployee:
    finance_emp_id: int
    emp_id: int
    is_active: bool
    created_at: Optional[datetime]
    last_active_at: Optional[datetime]
