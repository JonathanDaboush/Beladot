"""
refund_request.py

Model for refund request entity.
Represents a user's request for a refund, including reason, status, and items.
"""

from datetime import datetime

class RefundRequest:
    def __init__(self, refund_request_id, order_id, order_item_ids, reason, status, date_of_request=None, description=None):
        """
        Initialize RefundRequest.
        Args:
            refund_request_id (int): Unique identifier for the refund request.
            order_id (int): Associated order ID.
            order_item_ids (list): List of order item IDs.
            reason (str): Reason for the refund.
            status (str): Status of the refund ('pending', 'approved', 'denied').
            date_of_request (datetime, optional): Date of the request.
            description (str, optional): Optional description field.
        """
        self.refund_request_id = refund_request_id
        self.order_id = order_id
        self.order_item_ids = order_item_ids  # List of order item IDs
        self.reason = reason
        self.status = status  # 'pending', 'approved', 'denied'
        self.date_of_request = date_of_request or datetime.now()
        self.description = description  # Optional description field
