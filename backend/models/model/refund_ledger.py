"""
refund_ledger.py

Model for refund ledger entity.
Represents a ledger entry for refund actions and amounts.
"""

from datetime import datetime

class RefundLedger:
    def __init__(self, refund_id, action, amount, timestamp=None):
        """
        Initialize RefundLedger.
        Args:
            refund_id (int): Associated refund ID.
            action (str): Action taken ('approved', 'rejected', etc.).
            amount (float): Amount of the refund.
            timestamp (datetime, optional): Timestamp of the ledger entry.
        """
        self.refund_id = refund_id
        self.action = action  # 'approved', 'rejected', etc.
        self.amount = amount
        self.timestamp = timestamp or datetime.now()
