"""
refund.py

Model for refund entity.
Represents a refund record, including payment, order item, amount, and approval details.
"""

class Refund:
    def __init__(self, refund_id, payment_id, order_item_id, amount, reason, approved_by_cs_id, status, created_at, processed_at):
        """
        Initialize Refund.
        Args:
            refund_id (int): Unique identifier for the refund.
            payment_id (int): Associated payment ID.
            order_item_id (int): Associated order item ID.
            amount (float): Refund amount.
            reason (str): Reason for the refund.
            approved_by_cs_id (int): Customer service approver ID.
            status (str): Refund status.
            created_at (datetime): Creation timestamp.
            processed_at (datetime): Processing timestamp.
        """
        self.refund_id = refund_id
        self.payment_id = payment_id
        self.order_item_id = order_item_id
        self.amount = amount
        self.reason = reason
        self.approved_by_cs_id = approved_by_cs_id
        self.status = status
        self.created_at = created_at
        self.processed_at = processed_at
