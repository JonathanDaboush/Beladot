
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from backend.model.base import Base
from backend.model.enums import AvailabilityStatus

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(String(1024))
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id', ondelete='CASCADE'), nullable=False, index=True)
    subcategory_id = Column(Integer, ForeignKey('subcategory.id', ondelete='SET NULL'), index=True)
    is_available = Column(Enum(AvailabilityStatus), default=AvailabilityStatus.AVAILABLE, nullable=False)

    # Relationships (example)
    # category = relationship('Category', back_populates='products', lazy='selectin')

    __table_args__ = (
        Index('ix_product_category_id', 'category_id'),
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
