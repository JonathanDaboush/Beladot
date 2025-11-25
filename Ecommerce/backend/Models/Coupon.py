from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, CheckConstraint
from sqlalchemy.sql import func
from database import Base


class Coupon(Base):
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
