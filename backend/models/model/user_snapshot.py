from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class UserSnapshot:
    full_name: str
    email: str
    phone_number: str
    account_type: str
    bank: str
    approved_by_name: str
