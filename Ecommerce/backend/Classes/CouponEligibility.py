class CouponEligibility:
    def __init__(self, id, coupon_id, brand_id, product_id=None, product_variant_id=None, category_id=None):
        self.id = id
        self.coupon_id = coupon_id
        self.brand_id = brand_id
        self.product_id = product_id
        self.product_variant_id = product_variant_id
        self.category_id = category_id
    def __repr__(self):
        return f"<CouponEligibility(id={self.id}, coupon_id={self.coupon_id}, brand_id={self.brand_id}, product_id={self.product_id}, product_variant_id={self.product_variant_id}, category_id={self.category_id})>"
