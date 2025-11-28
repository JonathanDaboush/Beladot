from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, CheckConstraint
from sqlalchemy.sql import func
from database import Base


class Coupon(Base):
    """
    SQLAlchemy ORM model for coupons table.
    
    Promotional discount codes with flexible targeting and usage limits.
    Supports percentage discounts, fixed amount reductions, and free shipping.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Indexes: id (primary), code (unique), starts_at, expires_at
        
    Data Integrity:
        - Code must be unique and non-empty (e.g., "SAVE20")
        - Discount type: percentage, fixed, or free_shipping
        - Discount value must be non-negative
        - Expiration date must be after start date
        - Usage count cannot exceed usage limit
        - All monetary amounts in cents
        
    Discount Types:
        - percentage: Discount as % of cart total (e.g., 20% off)
        - fixed: Flat amount off (e.g., $5 off)
        - free_shipping: Waives shipping costs
        
    Usage Controls:
        - usage_limit: Global cap (e.g., first 100 customers)
        - per_user_limit: Per-customer cap (e.g., one per user)
        - usage_count: Tracks total redemptions
        - is_active: Manual enable/disable toggle
        
    Targeting:
        - min_purchase_amount_cents: Minimum cart value requirement
        - max_discount_amount_cents: Cap on discount (prevents abuse)
        - applicable_product_ids: JSON array of eligible product IDs
        - applicable_category_ids: JSON array of eligible category IDs
        
    Design Notes:
        - Code stored uppercase for case-insensitive matching
        - Time window: starts_at to expires_at
        - Empty targeting arrays = applies to all products
        - Percentage discounts capped by max_discount_amount_cents
        - Usage tracking enables "limited time" promotions
        
    Validation Flow:
        1. Check is_active and time window
        2. Verify usage limits not exceeded
        3. Validate cart meets min_purchase_amount
        4. Check product/category targeting
        5. Calculate discount (respect max_discount_amount)
        6. Increment usage_count on order completion
        
    Failure Modes:
        - Expired: expires_at < now()
        - Usage exceeded: usage_count >= usage_limit
        - Cart too small: total < min_purchase_amount_cents
        - Wrong products: Product not in applicable_product_ids
    """
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    discount_type = Column(String(20), nullable=False)
    discount_value_cents = Column(Integer, nullable=False)
    min_purchase_amount_cents = Column(Integer, nullable=True)
    max_discount_amount_cents = Column(Integer, nullable=True)
    applicable_product_ids = Column(JSON, nullable=True)
    applicable_category_ids = Column(JSON, nullable=True)
    usage_limit = Column(Integer, nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)
    per_user_limit = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    # New field for external coupon provider metadata (e.g., Honey, Rakuten, etc.)
    external_metadata = Column(JSON, nullable=True, comment="External coupon provider metadata (e.g., source, restrictions, provider info)")
    # Promotion fields
    promotion = Column(Boolean, default=False, nullable=False, comment="True if this coupon is an automatic promotion")
    promotion_metadata = Column(JSON, nullable=True, comment="Promotion metadata: schedule, budget, state, rules, targets, channels, exclusions, audit, usage, etc.")

    __table_args__ = (
        CheckConstraint("length(trim(code)) > 0", name='check_code_present'),
        CheckConstraint("discount_type IN ('percentage', 'fixed', 'free_shipping')", name='check_discount_type_valid'),
        CheckConstraint("discount_value_cents >= 0", name='check_discount_value_non_negative'),
        CheckConstraint("min_purchase_amount_cents IS NULL OR min_purchase_amount_cents >= 0", name='check_min_purchase_non_negative'),
        CheckConstraint("max_discount_amount_cents IS NULL OR max_discount_amount_cents > 0", name='check_max_discount_positive'),
        CheckConstraint("usage_limit IS NULL OR usage_limit > 0", name='check_usage_limit_positive'),
        CheckConstraint("usage_count >= 0", name='check_usage_count_non_negative'),
        CheckConstraint("usage_limit IS NULL OR usage_count <= usage_limit", name='check_usage_not_exceeded'),
        CheckConstraint("per_user_limit IS NULL OR per_user_limit > 0", name='check_per_user_limit_positive'),
        CheckConstraint("expires_at > starts_at", name='check_expires_after_starts'),
        CheckConstraint("updated_at >= created_at", name='check_updated_after_created'),
    )

    def __repr__(self):
        return f"<Coupon(id={self.id}, code={self.code}, discount_value_cents={self.discount_value_cents})>"
