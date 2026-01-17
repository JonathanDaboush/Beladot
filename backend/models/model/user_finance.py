from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class UserFinance:
    uf_id: int
    user_id: int
    bank: str
    pin: str
    cvv: str
    credit_card_number: str
    account_type: Literal["checking", "savings", "credit"]
