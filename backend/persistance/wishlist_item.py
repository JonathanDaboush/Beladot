"""
wishlist_item.py

SQLAlchemy ORM model for the wishlist_item table.
Represents an item in a user's wishlist, including product, variant, and quantity.
"""

from sqlalchemy import Column, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class WishlistItem(Base):
    __tablename__ = 'wishlist_item'
    wishlist_item_id = Column(BigInteger, primary_key=True)
    wishlist_id = Column(BigInteger, ForeignKey('wishlist.wishlist_id'))
    product_id = Column(BigInteger, ForeignKey('product.product_id'))
    variant_id = Column(BigInteger, ForeignKey('product_variant.variant_id'), nullable=True)
    quantity = Column(Integer)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))  # Updated ForeignKey reference
    user = relationship('User', back_populates='wishlist_items')  # Added relationship reference
