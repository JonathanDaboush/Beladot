from typing import Any, Optional
from datetime import datetime, timezone

class Coupon:
    def __init__(self, id, code, description, discount_type, discount_value_cents, min_purchase_amount_cents, max_discount_amount_cents, applicable_product_ids, applicable_category_ids, usage_limit, usage_count, per_user_limit, is_active, starts_at, expires_at, created_at, updated_at):
        self.id = id
        self.code = code
        self.description = description
        self.discount_type = discount_type
        self.discount_value_cents = discount_value_cents
        self.min_purchase_amount_cents = min_purchase_amount_cents
        self.max_discount_amount_cents = max_discount_amount_cents
        self.applicable_product_ids = applicable_product_ids
        self.applicable_category_ids = applicable_category_ids
        self.usage_limit = usage_limit
        self.usage_count = usage_count
        self.per_user_limit = per_user_limit
        self.is_active = is_active
        self.starts_at = starts_at
        self.expires_at = expires_at
        self.created_at = created_at
        self.updated_at = updated_at
    
    def validate_for_cart(self, cart, user_id: Optional[str], user_usage_repository=None) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        
        if not self.is_active:
            return {"valid": False, "reason": "Coupon is not active", "discount_cents": 0}
        
        if self.starts_at and now < self.starts_at:
            return {"valid": False, "reason": "Coupon is not yet valid", "discount_cents": 0}
        
        if self.expires_at and now > self.expires_at:
            return {"valid": False, "reason": "Coupon has expired", "discount_cents": 0}
        
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return {"valid": False, "reason": "Coupon usage limit reached", "discount_cents": 0}
        
        cart_subtotal = sum(item.line_total_cents() for item in cart._items)
        
        if self.min_purchase_amount_cents and cart_subtotal < self.min_purchase_amount_cents:
            return {
                "valid": False,
                "reason": f"Minimum purchase of ${self.min_purchase_amount_cents / 100:.2f} required",
                "discount_cents": 0
            }
        
        if self.per_user_limit and user_id and user_usage_repository:
            user_usage = user_usage_repository.get_coupon_usage_count(user_id, self.id)
            if user_usage >= self.per_user_limit:
                return {"valid": False, "reason": "Per-user usage limit reached", "discount_cents": 0}
        
        applicable_total = 0
        if self.applicable_product_ids or self.applicable_category_ids:
            for item in cart._items:
                item_applies = False
                if self.applicable_product_ids and item.product_id in self.applicable_product_ids:
                    item_applies = True
                if self.applicable_category_ids and hasattr(item, 'category_id') and item.category_id in self.applicable_category_ids:
                    item_applies = True
                if item_applies:
                    applicable_total += item.line_total_cents()
        else:
            applicable_total = cart_subtotal
        
        if applicable_total == 0:
            return {"valid": False, "reason": "No applicable items in cart", "discount_cents": 0}
        
        discount_cents = self._calculate_discount(applicable_total)
        
        return {
            "valid": True,
            "reason": "Coupon applied successfully",
            "discount_cents": discount_cents
        }
    
    def _calculate_discount(self, applicable_total: int) -> int:
        if self.discount_type == "percentage":
            discount = int((applicable_total * self.discount_value_cents) / 10000)
        elif self.discount_type == "fixed":
            discount = self.discount_value_cents
        elif self.discount_type == "free_shipping":
            discount = 0
        else:
            discount = 0
        
        if self.max_discount_amount_cents and discount > self.max_discount_amount_cents:
            discount = self.max_discount_amount_cents
        
        discount = min(discount, applicable_total)
        
        return discount
    
    def apply_to_cart(self, cart) -> int:
        validation = self.validate_for_cart(cart, cart.user_id)
        
        if not validation["valid"]:
            return 0
        
        discount_cents = validation["discount_cents"]
        
        if self.code not in cart._coupons:
            cart._coupons.append(self.code)
        
        return discount_cents