
# ------------------------------------------------------------------------------
# seller_review_response.py
# ------------------------------------------------------------------------------
# SQLAlchemy ORM model for the seller_review_response table.
# This module defines the SellerReviewResponse class, which represents a seller's
# response to a product review. Tracks review, seller, response text, and timestamp.
# ------------------------------------------------------------------------------

from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class SellerReviewResponse(Base):
    """
    ORM model for the 'seller_review_response' table.
    Represents a seller's response to a product review.

    Attributes:
        response_id (BigInteger): Primary key for the response.
        review_id (BigInteger): Foreign key referencing the product review.
        seller_id (BigInteger): Foreign key referencing the seller (user).
        response_text (Text): Text content of the seller's response.
        created_at (DateTime): Timestamp when the response was created.
        # Relationships to product_review are defined elsewhere.
    """
    __tablename__ = 'seller_review_response'
    response_id = Column(BigInteger, primary_key=True)
    review_id = Column(BigInteger, ForeignKey('product_review.review_id'))
    seller_id = Column(BigInteger, ForeignKey('users.user_id'))
    response_text = Column(Text)
    created_at = Column(DateTime)
    # Relationships (to be completed in product_review.py)
