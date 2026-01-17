
# ------------------------------------------------------------------------------
# product_comment.py
# ------------------------------------------------------------------------------
# SQLAlchemy ORM model for the product_comment table.
# Represents a user's comment on a product with soft-delete support.
# ------------------------------------------------------------------------------

from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Boolean, ForeignKey
from backend.db.base import Base

class ProductComment(Base):
    """
    ORM model for the 'product_comment' table.

    Attributes:
        comment_id (BigInteger): Primary key for the comment.
        product_id (BigInteger): Foreign key referencing the product.
        user_id (BigInteger): Foreign key referencing the user.
        comment (String): The comment text.
        created_at (DateTime): Timestamp when the comment was created.
        is_deleted (Boolean): Soft delete flag.
    """
    __tablename__ = 'product_comment'
    comment_id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey('product.product_id'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('user.user_id'), nullable=False)
    comment = Column(String(1000), nullable=False)
    created_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
