
# ------------------------------------------------------------------------------
# refund.py
# ------------------------------------------------------------------------------
# SQLAlchemy ORM model for the refund table.
# This module defines the Refund class, which represents a refund transaction.
# Tracks payment, order item, amount, reason, approval, status, and timestamps.
# ------------------------------------------------------------------------------

from sqlalchemy import Column, BigInteger, Numeric, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .enums import RefundStatusEnum
from . import payment  # ensure payment table is registered in metadata

class Refund(Base):
    """
    ORM model for the 'refund' table.
    Represents a refund transaction.

    Attributes:
        refund_id (BigInteger): Primary key for the refund.
        payment_id (BigInteger): Foreign key referencing the payment.
        order_item_id (BigInteger): Foreign key referencing the order item (optional).
        amount (Numeric): Amount refunded.
        reason (Text): Reason for the refund.
        approved_by_cs_id (BigInteger): Foreign key referencing the approving customer service employee (optional).
        status (Enum): Status of the refund (see RefundStatusEnum).
        created_at (DateTime): Timestamp when the refund was created.
        processed_at (DateTime): Timestamp when the refund was processed.
        # Relationships to payment, order_item, and employee are defined elsewhere.
    """
    __tablename__ = 'refund'
    refund_id = Column(BigInteger, primary_key=True)
    payment_id = Column(BigInteger, ForeignKey('payment.payment_id'))
    order_item_id = Column(BigInteger, ForeignKey('order_item.order_item_id'), nullable=True)
    amount = Column(Numeric(10,2))
    reason = Column(Text)
    approved_by_cs_id = Column(BigInteger, ForeignKey('employee.emp_id'), nullable=True)
    status = Column(Enum(RefundStatusEnum))
    created_at = Column(DateTime)
    processed_at = Column(DateTime)
    # Relationships (to be completed in payment.py, order_item.py, employee.py)
