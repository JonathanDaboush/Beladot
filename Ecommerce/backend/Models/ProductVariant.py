from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base


class ProductVariant(Base):
    """
    SQLAlchemy ORM model for product_variants table.
    
    Represents specific SKUs of a product with different attributes (size, color, etc.).
    Supports independent pricing, inventory, and up to 3 option dimensions per variant.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Key: product_id -> products.id (CASCADE)
        - Indexes: id (primary), product_id, sku (unique)
        
    Data Integrity:
        - SKU must be unique across all variants
        - Name and SKU cannot be empty
        - Price must be non-negative
        - Compare-at price (MSRP) must be >= selling price
        - Cost must be non-negative
        - Stock quantity must be non-negative
        - Option pairs must be complete (name + value together or both NULL)
        - Inventory policy: 'deny' (prevent oversell) or 'continue' (allow backorder)
        
    Relationships:
        - Many-to-one with Product (product has many variants)
        
    Variant Options:
        - Supports up to 3 option dimensions
        - option1: Size (e.g., "Size": "Large")
        - option2: Color (e.g., "Color": "Blue")
        - option3: Material (e.g., "Material": "Cotton")
        - Each option requires both name and value (enforced by constraints)
        
    Pricing:
        - price_cents: Current selling price
        - compare_at_price_cents: Original/MSRP price (for "was $X, now $Y")
        - cost_cents: Wholesale/unit cost (for profit margin calculation)
        
    Inventory Management:
        - stock_quantity: Available units
        - track_stock: Enable/disable inventory tracking
        - inventory_management: System managing stock ("shopify", "custom", etc.)
        - inventory_policy:
          * "deny": Prevent purchase when out of stock
          * "continue": Allow backorders/pre-orders
        
    Design Notes:
        - SKU: Unique identifier for inventory/shipping systems
        - name: Display name (e.g., "Large Blue Cotton T-Shirt")
        - Variant without options: Simple product (1 variant)
        - Product with variants: Options create variant matrix
        
    Example Variant Matrix:
        Product: T-Shirt
        - Variant 1: option1="Size":"S", option2="Color":"Red"
        - Variant 2: option1="Size":"S", option2="Color":"Blue"
        - Variant 3: option1="Size":"M", option2="Color":"Red"
        - Variant 4: option1="Size":"M", option2="Color":"Blue"
        
    Stock Tracking:
        - track_stock = true: Decrement on purchase, prevent oversell
        - track_stock = false: Unlimited availability (digital products, services)
        
    Profit Margin:
        - margin = price_cents - cost_cents
        - margin% = ((price - cost) / price) × 100
    """
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
