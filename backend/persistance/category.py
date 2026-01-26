
# ------------------------------------------------------------------------------
# category.py
# ------------------------------------------------------------------------------
# SQLAlchemy ORM model for the category table.
# This module defines the Category class, which represents a product category.
# Each category can have a name and an optional image URL. Relationships to
# subcategories and products are defined elsewhere.
# ------------------------------------------------------------------------------

from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship
from .base import Base

class Category(Base):
    """
    ORM model for the 'category' table.
    Represents a product category in the catalog.

    Attributes:
        category_id (BigInteger): Primary key for the category.
        name (String): Name of the category.
        image_url (String): URL to an image representing the category (optional).
        # Relationships to subcategories and products are defined elsewhere.
    """
    __tablename__ = 'category'
    category_id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    image_url = Column(String(255), nullable=True)
    subcategories = relationship(
        "Subcategory",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
