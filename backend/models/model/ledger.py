"""
ledger.py

Domain model for ledger entries (pure dataclass).
Represents a financial transaction or event in the system ledger.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from backend.models.model.domain_event import DomainEvent

@dataclass(slots=True)
class LedgerEntry:
    entry_type: str  # credit, debit, refund, adjustment
    amount: float
    event_ref: DomainEvent
    actor: str
    timestamp: Optional[datetime] = None
