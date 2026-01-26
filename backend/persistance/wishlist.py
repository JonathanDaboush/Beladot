"""
wishlist.py

SQLAlchemy ORM model for the wishlist table.
Represents a user's wishlist, including creation and update timestamps.
"""

from sqlalchemy import Column, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Wishlist(Base):
    __tablename__ = 'wishlist'
    wishlist_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    # Relationships (to be completed in wishlist_item.py)
