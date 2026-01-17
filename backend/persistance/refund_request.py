
"""
refund_request.py

SQLAlchemy ORM model for refund requests.
Represents a customer's request for a refund, including the items involved,
reason, status, and optional description. Stores `order_item_ids` as a JSON
string to avoid join proliferation in test environment.
"""

from sqlalchemy import Column, BigInteger, Text, DateTime, String, ForeignKey
from sqlalchemy.orm import validates
from .base import Base

class RefundRequest(Base):
    __tablename__ = 'refund_request'
    refund_request_id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey('order.order_id'), nullable=False)
    # JSON array of order item ids
    order_item_ids = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(32), nullable=False)
    date_of_request = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)

    @validates('order_item_ids')
    def _validate_order_item_ids(self, key, value):
        import json
        if isinstance(value, (list, tuple)):
            return json.dumps(list(value))
        if isinstance(value, str):
            return value
        raise ValueError('order_item_ids must be a list or JSON string')

    def get_order_item_ids(self):
        import json
        try:
            return json.loads(self.order_item_ids) if self.order_item_ids else []
        except Exception:
            return []
