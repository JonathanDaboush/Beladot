
# ------------------------------------------------------------------------------
# product_review.py
# ------------------------------------------------------------------------------
# SQLAlchemy ORM model for the product_review table.
# This module defines the ProductReview class, which represents a review written
# by a user for a product. Tracks review text, rating, and creation timestamp.
# ------------------------------------------------------------------------------

from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ProductReview(Base):
    """
    ORM model for the 'product_review' table.
    Represents a review written by a user for a product.

    Attributes:
        review_id (BigInteger): Primary key for the review.
        product_id (BigInteger): Foreign key referencing the product.
        user_id (BigInteger): Foreign key referencing the user who wrote the review.
        rating_id (BigInteger): Foreign key referencing the associated product rating.
        review_text (Text): Text content of the review.
        created_at (DateTime): Timestamp when the review was created.
        # Relationships to related models are defined elsewhere.
    """
    __tablename__ = 'product_review'
    review_id = Column(BigInteger, primary_key=True)
    product_id = Column(BigInteger, ForeignKey('product.product_id'))
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    rating_id = Column(BigInteger, ForeignKey('product_rating.rating_id'))
    review_text = Column(Text)
    created_at = Column(DateTime)
    # Relationships (to be completed in related models)
