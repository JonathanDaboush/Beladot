"""
ledger.py

Model for ledger entry entity.
Represents a financial transaction or event in the system ledger.
"""

from backend.model.domain_event import DomainEvent, DomainEventType
from backend.model.enums import EmployeePaymentStatus
from datetime import datetime

class LedgerEntry:
    def __init__(self, entry_type, amount, event_ref, actor, timestamp=None):
        """
        Initialize LedgerEntry.
        Args:
            entry_type (str): Type of entry (credit, debit, refund, adjustment).
            amount (float): Transaction amount.
            event_ref (DomainEvent): Reference to the domain event.
            actor (str): Actor who performed the transaction.
            timestamp (datetime, optional): Transaction timestamp.
        """
        self.entry_type = entry_type  # credit, debit, refund, adjustment
        self.amount = amount
        self.event_ref = event_ref  # DomainEvent reference
        self.actor = actor
        self.timestamp = timestamp or datetime.utcnow()
