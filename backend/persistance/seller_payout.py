
# ------------------------------------------------------------------------------
# seller_payout.py
# ------------------------------------------------------------------------------
# SQLAlchemy ORM model for the seller_payout table.
# This module defines the SellerPayout class, which represents a payout made to
# a seller. Tracks seller, amount, currency, status, and timestamps.
# ------------------------------------------------------------------------------

from sqlalchemy import Column, BigInteger, Numeric, String, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .enums import PayoutStatusEnum

class SellerPayout(Base):
    """
    ORM model for the 'seller_payout' table.
    Represents a payout made to a seller.

    Attributes:
        payout_id (BigInteger): Primary key for the payout.
        seller_id (BigInteger): Foreign key referencing the seller (user).
        amount (Numeric): Amount paid to the seller.
        currency (String): Currency of the payout.
        date_of_payment (Date): Date the payout was made.
        status (Enum): Status of the payout (see PayoutStatusEnum).
        created_at (DateTime): Timestamp when the payout record was created.
        # Relationships to user are defined elsewhere.
    """
    __tablename__ = 'seller_payout'
    payout_id = Column(BigInteger, primary_key=True)
    seller_id = Column(BigInteger, ForeignKey('users.user_id'))
    amount = Column(Numeric(10,2))
    currency = Column(String(10))
    date_of_payment = Column(Date)
    status = Column(Enum(PayoutStatusEnum))
    created_at = Column(DateTime)
    # Relationships (to be completed in user.py)
