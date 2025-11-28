from sqlalchemy import Column, Integer, ForeignKey
from database import Base

class CouponEligibility(Base):
    __tablename__ = "coupon_eligibility"
    id = Column(Integer, primary_key=True, autoincrement=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=True)
    product_variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True)

    def __repr__(self):
        return f"<CouponEligibility(id={self.id}, coupon_id={self.coupon_id}, brand_id={self.brand_id}, product_id={self.product_id}, product_variant_id={self.product_variant_id}, category_id={self.category_id})>"
