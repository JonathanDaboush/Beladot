from __future__ import annotations

from dataclasses import dataclass
from .enums import ShiftRequestStatus


@dataclass(slots=True)
class ShiftRequest:
    shift_request_id: int
    shift_id: int
    requesting_emp_id: int
    approved_by_manager_id: int
    status: ShiftRequestStatus
