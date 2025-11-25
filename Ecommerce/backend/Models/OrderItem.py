from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)
    product_name = Column(String(255), nullable=False)
    product_sku = Column(String(100), nullable=False)
    variant_name = Column(String(100), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price_cents = Column(Integer, nullable=False)
    total_price_cents = Column(Integer, nullable=False)
    discount_cents = Column(Integer, default=0, nullable=False)
    tax_cents = Column(Integer, default=0, nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")
    shipment_items = relationship("ShipmentItem", back_populates="order_item")
    
    __table_args__ = (
        CheckConstraint("length(trim(product_name)) > 0", name='check_product_name_present'),
        CheckConstraint("length(trim(product_sku)) > 0", name='check_product_sku_present'),
        CheckConstraint("quantity > 0", name='check_quantity_positive'),
        CheckConstraint("unit_price_cents >= 0", name='check_unit_price_non_negative'),
        CheckConstraint("discount_cents >= 0", name='check_discount_non_negative'),
        CheckConstraint("tax_cents >= 0", name='check_tax_non_negative'),
        CheckConstraint("total_price_cents >= 0", name='check_total_price_non_negative'),
        CheckConstraint("total_price_cents = (quantity * unit_price_cents) - discount_cents + tax_cents", name='check_total_price_equals_calculation'),
    )
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_name={self.product_name})>"
