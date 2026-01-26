"""
subcategory.py

SQLAlchemy ORM model for the subcategory table.
Represents a subcategory within a category, including name and image URL.
"""

from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Subcategory(Base):
    __tablename__ = 'subcategory'
    subcategory_id = Column(BigInteger, primary_key=True)
    category_id = Column(BigInteger, ForeignKey('category.category_id'))
    name = Column(String(100), nullable=False)
    image_url = Column(String(255), nullable=True)
    category = relationship(
        "Category",
        back_populates="subcategories",
        lazy="selectin"
    )
