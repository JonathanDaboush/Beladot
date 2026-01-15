"""
category.py

Model for product category entity.
Represents a product category with optional image URL.
"""


from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.orm import relationship
from backend.model.base import Base

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True, index=True)
    image_url = Column(String(256))

    # Relationships (example)
    # products = relationship('Product', back_populates='category', lazy='selectin')

    __table_args__ = (
        Index('ix_category_name', 'name'),
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
