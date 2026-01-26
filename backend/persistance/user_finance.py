"""
user_finance.py

SQLAlchemy ORM model for the user_finance table.
Represents a user's financial information, including bank, card, and account type.
"""

from sqlalchemy import Column, BigInteger, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import Base
from .enums import AccountTypeEnum

class UserFinance(Base):
    __tablename__ = 'user_finance'
    uf_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    bank = Column(String(100))
    pin = Column(String(4))
    cvv = Column(String(3))
    credit_card_number = Column(String(16))
    account_type = Column(Enum(AccountTypeEnum))
    # Relationship (to be completed in user.py)
