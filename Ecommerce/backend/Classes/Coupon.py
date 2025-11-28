from typing import Any, Optional
from datetime import datetime, timezone

class Coupon:
    """
    Domain model representing a promotional coupon with validation and discount calculation.
    
    This class manages coupon codes, validation rules, and discount calculations. It supports
    multiple discount types (percentage, fixed, free shipping), usage limits, product/category
    restrictions, and time-based validity.
    
    Key Responsibilities:
        - Store coupon configuration (code, type, value, limits)
        - Validate coupon applicability to carts
        - Calculate discount amounts
        - Enforce usage limits (global and per-user)
        - Support time-based activation/expiration
        - Apply product/category restrictions
    
    Discount Types:
        - percentage: Discount as percentage (e.g., 15% off)
        - fixed: Fixed amount off (e.g., $10 off)
        - free_shipping: Free shipping (discount calculated by shipping service)
    
    Validation Rules:
        - Must be active and within valid date range
        - Cannot exceed global or per-user usage limits
        - Must meet minimum purchase requirement
        - Must apply to at least one cart item (for restricted coupons)
    
    Design Notes:
        - Prices stored in cents (avoids floating-point errors)
        - discount_value_cents meaning depends on discount_type
        - For percentage: stored as basis points (1500 = 15%)
        - For fixed: stored as cents (1500 = $15.00)
        - This is a domain object; persistence handled by CouponRepository
    """
    def __init__(self, id, code, description, discount_type, discount_value_cents, min_purchase_amount_cents, max_discount_amount_cents, applicable_product_ids, applicable_category_ids, usage_limit, usage_count, per_user_limit, is_active, starts_at, expires_at, created_at, updated_at, external_metadata=None, promotion=False, promotion_metadata=None):
        """
        Initialize a Coupon domain object.
        
        Args:
            id: Unique identifier (None for new coupons before persistence)
            code: Coupon code (e.g., 'SAVE15', 'FREESHIP')
            description: Human-readable description
            discount_type: Type of discount ('percentage', 'fixed', 'free_shipping')
            discount_value_cents: Discount amount (meaning depends on type)
            min_purchase_amount_cents: Minimum cart total required (None for no minimum)
            max_discount_amount_cents: Maximum discount cap (None for unlimited)
            applicable_product_ids: List of product IDs (None/empty for all products)
            applicable_category_ids: List of category IDs (None/empty for all categories)
            usage_limit: Global usage limit (None for unlimited)
            usage_count: Current number of times used
            per_user_limit: Per-user usage limit (None for unlimited)
            is_active: Whether coupon is currently active
            starts_at: Activation timestamp (None for immediate)
            expires_at: Expiration timestamp (None for no expiration)
            created_at: Coupon creation timestamp
            updated_at: Last modification timestamp
            external_metadata: Dict or JSON with external coupon provider metadata (e.g., source, restrictions, provider info)
            promotion: Boolean, True if this is an automatic promotion
            promotion_metadata: Dict or JSON with promotion metadata (schedule, rules, targets, etc.)
        """
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
        self.external_metadata = external_metadata
        self.promotion = promotion
        self.promotion_metadata = promotion_metadata
    
    def validate_for_cart(self, cart, user_id: Optional[str], user_usage_repository=None) -> dict[str, Any]:
        """
        Validate coupon applicability to a cart and calculate discount.
        
        Args:
            cart: Cart object to validate against
            user_id: User ID for per-user limit checking (optional)
            user_usage_repository: Repository for querying user's coupon usage (optional)
            
        Returns:
            dict: Validation result with keys:
                - valid (bool): Whether coupon can be applied
                - reason (str): Success message or failure reason
                - discount_cents (int): Calculated discount amount
                
        Validation Checks (in order):
            1. Coupon must be active
            2. Current time must be after starts_at
            3. Current time must be before expires_at
            4. Global usage limit not exceeded
            5. Cart subtotal meets minimum purchase requirement
            6. Per-user usage limit not exceeded (if user_id provided)
            7. At least one cart item matches product/category restrictions
            
        Design Notes:
            - Validation fails fast (returns on first failure)
            - Per-user limit requires both user_id and repository
            - Product/category restrictions are OR logic (item matches either)
            - Empty restrictions mean coupon applies to all items
        """
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
        """
        Calculate discount amount based on coupon type and applicable total.
        
        Args:
            applicable_total: Sum of applicable cart items in cents
            
        Returns:
            int: Discount amount in cents
            
        Calculation Rules:
            - Percentage: (applicable_total × discount_value_cents) / 10000
            - Fixed: discount_value_cents (flat amount)
            - Free shipping: 0 (handled by shipping service)
            - Capped by max_discount_amount_cents if set
            - Cannot exceed applicable_total
            
        Design Notes:
            - Percentage uses basis points (10000 = 100%)
            - Integer division prevents fractional cents
            - Discount clamped to applicable total (prevents negative)
        """
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
        """
        Validate and apply coupon to cart, adding code to cart's coupon list.
        
        Args:
            cart: Cart object to apply coupon to
            
        Returns:
            int: Discount amount in cents (0 if invalid)
            
        Side Effects:
            - Adds coupon code to cart._coupons list if valid and not already present
            
        Design Notes:
            - Validation performed first (calls validate_for_cart)
            - Returns 0 for invalid coupons (doesn't raise exception)
            - Prevents duplicate coupon codes in cart
        """
        validation = self.validate_for_cart(cart, cart.user_id)
        
        if not validation["valid"]:
            return 0
        
        discount_cents = validation["discount_cents"]
        
        if self.code not in cart._coupons:
            cart._coupons.append(self.code)
        
        return discount_cents