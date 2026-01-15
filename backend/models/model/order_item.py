"""
order_item.py

Model for order item entity.
Represents an item within an order, including product and variant details.
"""


from sqlalchemy import Column, Integer, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.model.base import Base

class OrderItem(Base):
    __tablename__ = 'order_item'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('product.id', ondelete='CASCADE'), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey('product_variant.id', ondelete='SET NULL'), index=True)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)

    __table_args__ = (
        Index('ix_order_item_order_id', 'order_id'),
        Index('ix_order_item_product_id', 'product_id'),
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
