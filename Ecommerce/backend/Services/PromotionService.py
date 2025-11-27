from typing import Any
from uuid import UUID

from Ecommerce.backend.Classes import Coupon as coupon, Cart as cart
from Ecommerce.backend.Repositories import CouponRepository as couponrepository

class PromotionService:
    """
    Promotions and Coupons Service
    Encapsulates business rules around promotions and coupons with stacking and precedence logic.
    Evaluates active promotions against a cart, computes discounts deterministically,
    enforces usage limits, and returns explanations sufficient for UX.
    Promotions must be testable in isolation and applied in deterministic order.
    """
    
    def __init__(self, coupon_repository, promotion_repository):
        self.coupon_repository = coupon_repository
        self.promotion_repository = promotion_repository
    
    def validate_coupon(self, code: str, cart, user_id: UUID | None) -> dict:
        """
        Read-only evaluation of coupon applicability and calculation of potential discount.
        Return {valid, reason, discount_cents}.
        Must enforce start/expiry, min order value, and per-user single-use logic
        without mutating uses_count.
        """
        pass
    
    def apply_promotions(self, cart) -> int:
        """
        Run all relevant promotions against the cart and compute order-level discount in cents.
        This is a pure function used by PricingService to include promotions in totals.
        """
        pass
    
    def evaluate_cart_for_promos(self, cart) -> list[dict]:
        """
        Return detail list of applied promotions with breakpoints,
        for admin visibility and debugging.
        """
        pass
