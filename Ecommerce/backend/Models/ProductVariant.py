from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    price_cents = Column(Integer, nullable=False)
    compare_at_price_cents = Column(Integer, nullable=True)
    cost_cents = Column(Integer, nullable=True)
    stock_quantity = Column(Integer, default=0, nullable=False)
    inventory_management = Column(String(50), nullable=True)
    inventory_policy = Column(String(20), default="deny", nullable=False)
    track_stock = Column(Boolean, default=True, nullable=False)
    option1_name = Column(String(50), nullable=True)
    option1_value = Column(String(50), nullable=True)
    option2_name = Column(String(50), nullable=True)
    option2_value = Column(String(50), nullable=True)
    option3_name = Column(String(50), nullable=True)
    option3_value = Column(String(50), nullable=True)
    
    product = relationship("Product", back_populates="variants")
    
    __table_args__ = (
        CheckConstraint("length(trim(sku)) > 0", name='check_sku_present'),
        CheckConstraint("length(trim(name)) > 0", name='check_name_present'),
        CheckConstraint("price_cents >= 0", name='check_price_non_negative'),
        CheckConstraint("compare_at_price_cents IS NULL OR compare_at_price_cents >= price_cents", name='check_compare_price_higher'),
        CheckConstraint("cost_cents IS NULL OR cost_cents >= 0", name='check_cost_non_negative'),
        CheckConstraint("stock_quantity >= 0", name='check_stock_non_negative'),
        CheckConstraint("inventory_policy IN ('deny', 'continue')", name='check_inventory_policy_valid'),
        CheckConstraint("(option1_name IS NULL AND option1_value IS NULL) OR (option1_name IS NOT NULL AND option1_value IS NOT NULL)", name='check_option1_complete'),
        CheckConstraint("(option2_name IS NULL AND option2_value IS NULL) OR (option2_name IS NOT NULL AND option2_value IS NOT NULL)", name='check_option2_complete'),
        CheckConstraint("(option3_name IS NULL AND option3_value IS NULL) OR (option3_name IS NOT NULL AND option3_value IS NOT NULL)", name='check_option3_complete'),
    )
    
    def __repr__(self):
        return f"<ProductVariant(id={self.id}, product_id={self.product_id}, name={self.name})>"
