from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .enums import EmployeePaymentStatus


@dataclass(slots=True)
class EmployeePayment:
    payment_id: int
    emp_id: int
    amount: float
    payment_type: str
    status: EmployeePaymentStatus
    processed_by_finance_emp_id: Optional[int]
    created_at: Optional[datetime]
    paid_at: Optional[datetime]
