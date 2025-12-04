from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.orm import relationship
from database import Base


class OrderItem(Base):
    """
    SQLAlchemy ORM model for order_items table.
    
    Immutable snapshot of purchased products within an order. Stores denormalized
    product data to preserve historical accuracy even if products change or are deleted.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Keys: order_id -> orders.id (CASCADE), product_id -> products.id (SET NULL),
                       variant_id -> product_variants.id (SET NULL)
        - Indexes: id (primary), order_id
        
    Data Integrity:
        - Quantity must be positive
        - All prices must be non-negative
        - Total price calculated as: (quantity × unit_price) - discount + tax
        - Product name and SKU required (even if product deleted)
        - Check constraint enforces total_price calculation
        
    Relationships:
        - Many-to-one with Order (order contains many items)
        - Many-to-one with Product (nullable, for reporting)
        - Many-to-one with ProductVariant (nullable, for variant tracking)
        - One-to-many with ShipmentItem (for partial fulfillment)
        
    Denormalization Strategy:
        - product_name: Snapshot of name at purchase time
        - product_sku: Snapshot of SKU at purchase time
        - variant_name: Snapshot of variant description
        - unit_price_cents: Price paid (not current price)
        - Foreign keys SET NULL on delete (preserves order history)
        
    Price Components:
        - unit_price_cents: Base price per unit
        - quantity: Number of units purchased
        - discount_cents: Per-item discount (e.g., coupon, bulk discount)
        - tax_cents: Sales tax for this line item
        - total_price_cents: Final amount = (quantity × unit_price) - discount + tax
        
    Design Notes:
        - Immutable after order placement (no updates)
        - Product deletion doesn't break order history
        - SKU enables inventory system integration
        - Variant info captured for reporting and analytics
        - Shipment tracking via shipment_items relationship
        
    Fulfillment:
        - ShipmentItems link to this OrderItem with quantities
        - Supports partial shipments (split across multiple shipments)
        - Example: Order 10 units → Ship 6, then ship 4
        
    Reporting:
        - Revenue: SUM(total_price_cents) GROUP BY product_id
        - Best sellers: SUM(quantity) GROUP BY product_id ORDER BY DESC
        - Average order value: AVG(total_price_cents) per order
    """
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
    paid_out = Column(Boolean, default=False, nullable=False, index=True)  # For seller payout tracking
    
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
