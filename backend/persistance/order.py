
# ------------------------------------------------------------------------------
# order.py
# ------------------------------------------------------------------------------
# SQLAlchemy ORM model for the order table.
# This module defines the Order class, which represents a customer order. Tracks
# user, cart, status, total amount, and timestamps. Relationships to order items
# and related models are defined elsewhere.
# ------------------------------------------------------------------------------

from sqlalchemy import Column, BigInteger, Numeric, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .enums import OrderStatusEnum

class Order(Base):
    """
    ORM model for the 'order' table.
    Represents a customer order.

    Attributes:
        order_id (BigInteger): Primary key for the order.
        user_id (BigInteger): Foreign key referencing the user who placed the order.
        cart_id (BigInteger): Foreign key referencing the cart (optional).
        order_status (Enum): Status of the order (see OrderStatusEnum).
        total_amount (Numeric): Total amount for the order.
        created_at (DateTime): Timestamp when the order was created.
        updated_at (DateTime): Timestamp when the order was last updated.
        order_number (BigInteger): Unique order number for reference.
        # Relationships to order items and related models are defined elsewhere.
    """
    __tablename__ = 'order'
    order_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    cart_id = Column(BigInteger, ForeignKey('cart.cart_id'), nullable=True)
    order_status = Column(Enum(OrderStatusEnum))
    total_amount = Column(Numeric(10,2))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    order_number = Column(BigInteger)
    # Relationships (to be completed in related models)
