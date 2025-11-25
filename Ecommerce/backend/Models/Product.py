from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    price_cents = Column(Integer, nullable=False)
    compare_at_price_cents = Column(Integer, nullable=True)
    cost_cents = Column(Integer, nullable=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    stock_quantity = Column(Integer, default=0, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    weight = Column(Integer, nullable=True)
    dimensions = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="product")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    inventory_transactions = relationship("InventoryTransaction", back_populates="product", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name='check_name_present'),
        CheckConstraint("length(trim(slug)) > 0", name='check_slug_present'),
        CheckConstraint("length(trim(sku)) > 0", name='check_sku_present'),
        CheckConstraint("price_cents >= 0", name='check_price_non_negative'),
        CheckConstraint("compare_at_price_cents IS NULL OR compare_at_price_cents >= price_cents", name='check_compare_price_higher'),
        CheckConstraint("cost_cents IS NULL OR cost_cents >= 0", name='check_cost_non_negative'),
        CheckConstraint("stock_quantity >= 0", name='check_stock_non_negative'),
        CheckConstraint("weight IS NULL OR weight > 0", name='check_weight_positive'),
        CheckConstraint("updated_at >= created_at", name='check_updated_after_created'),
    )
    
    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price_cents})>"
