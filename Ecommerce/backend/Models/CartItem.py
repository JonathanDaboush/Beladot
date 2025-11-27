from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class CartItem(Base):
    """
    SQLAlchemy ORM model for cart_items table.
    
    Represents individual line items in shopping carts. Supports product variants,
    quantity tracking, and price snapshotting for accurate cart total calculation.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Keys: cart_id -> carts.id (CASCADE), product_id -> products.id (CASCADE),
                       variant_id -> product_variants.id (SET NULL)
        - Indexes: id (primary), cart_id, unique(cart_id, product_id, variant_id)
        
    Data Integrity:
        - Quantity must be positive (minimum 1)
        - Unit price must be non-negative (supports free items)
        - Unique constraint prevents duplicate product+variant combinations per cart
        - Cascading delete when cart or product deleted
        - Variant set to NULL if deleted (preserves cart history)
        
    Relationships:
        - Many-to-one with Cart (cart contains many items)
        - Many-to-one with Product (product can be in many carts)
        - Many-to-one with ProductVariant (optional, for size/color variants)
        
    Design Notes:
        - unit_price_cents: Snapshot at add-to-cart time (protects against price changes)
        - item_metadata: JSON storage for customization (engraving, gift wrap, etc.)
        - variant_id nullable: Supports simple products without variants
        - added_at: Timestamp enables "recently added" sorting and cart expiration
        - Unique constraint ensures single cart line per product+variant combo
        
    Price Calculation:
        - Line total = unit_price_cents * quantity
        - Cart total = sum of all CartItem line totals
        - Price changes don't affect existing cart items (snapshot behavior)
        
    Failure Modes:
        - Product deleted: CASCADE removes cart item automatically
        - Variant deleted: SET NULL preserves item (may become invalid)
        - Out of stock: Handled at checkout validation (not enforced here)
    """
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
