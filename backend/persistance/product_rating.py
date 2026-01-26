
# ------------------------------------------------------------------------------
# product_rating.py
# ------------------------------------------------------------------------------
# SQLAlchemy ORM model for the product_rating table.
# This module defines the ProductRating class, which represents a rating given
# by a user to a product. Tracks rating value and creation timestamp.
# ------------------------------------------------------------------------------

from sqlalchemy import Column, BigInteger, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ProductRating(Base):
    """
    ORM model for the 'product_rating' table.
    Represents a rating given by a user to a product.

    Attributes:
        rating_id (BigInteger): Primary key for the rating.
        product_id (BigInteger): Foreign key referencing the product.
        user_id (BigInteger): Foreign key referencing the user who gave the rating.
        rating (Integer): Rating value (e.g., 1-5 stars).
        created_at (DateTime): Timestamp when the rating was created.
        # Relationships to related models are defined elsewhere.
    """
    __tablename__ = 'product_rating'
    rating_id = Column(BigInteger, primary_key=True)
    product_id = Column(BigInteger, ForeignKey('product.product_id'))
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    rating = Column(Integer)
    created_at = Column(DateTime)
    # Relationships (to be completed in related models)
