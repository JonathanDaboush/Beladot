
# ------------------------------------------------------------------------------
# product.py
# ------------------------------------------------------------------------------
# SQLAlchemy ORM model for the product table.
# This module defines the Product class, which represents a product listed by a
# seller. Tracks category, subcategory, pricing, status, and timestamps.
# ------------------------------------------------------------------------------

from sqlalchemy import Column, Integer, BigInteger, String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Product(Base):
    """
    ORM model for the 'product' table.
    Represents a product listed by a seller.

    Attributes:
        product_id (BigInteger): Primary key for the product.
        seller_id (BigInteger): Foreign key referencing the seller (user).
        category_id (BigInteger): Foreign key referencing the product category.
        subcategory_id (BigInteger): Foreign key referencing the product subcategory.
        title (String): Title of the product.
        description (Text): Description of the product.
        price (Numeric): Price of the product.
        currency (String): Currency of the price.
        is_active (Boolean): Whether the product is currently active/listed.
        created_at (DateTime): Timestamp when the product was created.
        updated_at (DateTime): Timestamp when the product was last updated.
        # Relationships to related models are defined elsewhere.
    """
    __tablename__ = 'product'
    # Use Integer for SQLite autoincrement primary key behavior
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(BigInteger, ForeignKey('users.user_id'))
    category_id = Column(BigInteger, ForeignKey('category.category_id'))
    subcategory_id = Column(BigInteger, ForeignKey('subcategory.subcategory_id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10,2))
    currency = Column(String(10))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    # Relationships (to be completed in related models)
