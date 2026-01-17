"""
refund_ledger.py

Domain model for refund ledger entries (pure dataclass).
Represents a ledger entry for refund actions and amounts.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(slots=True)
class RefundLedger:
    refund_id: int
    action: str  # e.g., 'approved', 'rejected'
    amount: float
    timestamp: Optional[datetime] = None
