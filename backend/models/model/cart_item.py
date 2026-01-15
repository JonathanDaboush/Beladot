
from sqlalchemy import Column, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.model.base import Base

class CartItem(Base):
    __tablename__ = 'cart_item'
    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey('cart.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('product.id', ondelete='CASCADE'), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey('product_variant.id', ondelete='SET NULL'), index=True)
    quantity = Column(Integer, nullable=False)

    # Relationships (example)
    # cart = relationship('Cart', back_populates='items', lazy='selectin')

    __table_args__ = (
        Index('ix_cart_item_cart_id', 'cart_id'),
        Index('ix_cart_item_product_id', 'product_id'),
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
