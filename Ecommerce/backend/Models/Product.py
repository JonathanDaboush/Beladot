from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Product(Base):
    """
    SQLAlchemy ORM model for products table.
    
    Core catalog entity storing product information, pricing, and inventory.
    Supports variants (sizes, colors), images, and categorization.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Key: category_id -> categories.id (SET NULL on delete)
        - Unique Constraints: slug, sku
        - Indexes: id, name, slug, sku, category_id, is_active, created_at
        
    Data Integrity:
        - Name, slug, SKU must be non-empty
        - Prices non-negative, compare_at_price >= price if set
        - Stock quantity non-negative
        - Weight positive if set
        - updated_at >= created_at
        - Cascading relationships for images, variants, reviews
        
    Relationships:
        - Many-to-one with Category
        - One-to-many with ProductImage (cascade delete)
        - One-to-many with ProductVariant (cascade delete)
        - One-to-many with CartItem (no cascade, allows orphan cart items)
        - One-to-many with Review (cascade delete)
        - One-to-many with InventoryTransaction (cascade delete)
        
    Design Notes:
        - Prices stored in cents (avoids floating-point issues)
        - compare_at_price_cents enables strike-through pricing
        - cost_cents tracks COGS for margin analysis
        - slug used for SEO-friendly URLs (must be unique)
        - weight in grams, dimensions as string
        - Timestamps with timezone support
    """
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
    
    # Main categorization (catalog organization - e.g., Electronics -> Television)
    main_category_id = Column(Integer, ForeignKey("main_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    main_subcategory_id = Column(Integer, ForeignKey("main_subcategories.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Legacy category (deprecated, kept for backward compatibility)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id", ondelete="SET NULL"), nullable=True, index=True)
    
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    weight = Column(Integer, nullable=True)
    dimensions = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Main categorization relationships
    main_category = relationship("MainCategory", back_populates="products")
    main_subcategory = relationship("MainSubcategory", back_populates="products")
    
    # Legacy category relationship
    category = relationship("Category", back_populates="products")
    subcategory = relationship("Subcategory", back_populates="products")
    
    seller = relationship("Seller", back_populates="products")
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
