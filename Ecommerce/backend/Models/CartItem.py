from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price_cents = Column(Integer, nullable=False)
    item_metadata = Column(JSON, nullable=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")
    variant = relationship("ProductVariant")
    
    __table_args__ = (
        CheckConstraint("quantity > 0", name='check_quantity_positive'),
        CheckConstraint("unit_price_cents >= 0", name='check_unit_price_non_negative'),
        UniqueConstraint('cart_id', 'product_id', 'variant_id', name='unique_cart_product_variant'),
    )
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"
