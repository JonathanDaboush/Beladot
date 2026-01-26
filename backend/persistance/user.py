"""
user.py

SQLAlchemy ORM model for the user table.
Represents a user, including personal and account information.
"""

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from .base import Base
from .enums import SellerStatusEnum

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    dob = Column(Date)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20))
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(Date)
    img_location = Column(String(255))
    account_status = Column(String(5), nullable=False, default='True')
    # Relationships (to be completed in other models)
    wishlist_items = relationship(
        "WishlistItem",
        back_populates="user",
        cascade="all, delete-orphan"
    )
