# Represents a promotional discount code that customers can apply at checkout.
# Supports complex rules: percentage/fixed discounts, minimum purchase, usage limits, product/category restrictions, and time windows.
class Coupon:
    def __init__(self, id, code, description, discount_type, discount_value_cents, min_purchase_amount_cents, max_discount_amount_cents, applicable_product_ids, applicable_category_ids, usage_limit, usage_count, per_user_limit, is_active, starts_at, expires_at, created_at, updated_at):
        self.id = id  # Unique coupon identifier
        self.code = code  # Coupon code customers enter (e.g., "SAVE20", "FREESHIP") - must be unique
        self.description = description  # Internal description of promotion (e.g., "Black Friday 2024 - 20% off electronics")
        self.discount_type = discount_type  # How discount is calculated: "percentage" (e.g., 20% off) or "fixed" (e.g., $10 off)
        self.discount_value_cents = discount_value_cents  # Discount amount: for percentage, this is basis points (2000 = 20%), for fixed it's cents
        self.min_purchase_amount_cents = min_purchase_amount_cents  # Minimum cart total required to use coupon (in cents, null = no minimum)
        self.max_discount_amount_cents = max_discount_amount_cents  # Maximum discount allowed (caps percentage discounts, null = unlimited)
        self.applicable_product_ids = applicable_product_ids  # JSON array of product IDs coupon applies to (null/empty = all products)
        self.applicable_category_ids = applicable_category_ids  # JSON array of category IDs coupon applies to (null/empty = all categories)
        self.usage_limit = usage_limit  # Total number of times coupon can be used across all customers (null = unlimited)
        self.usage_count = usage_count  # How many times coupon has been used so far (increments with each order)
        self.per_user_limit = per_user_limit  # Max uses per customer (e.g., 1 = single-use per customer, null = unlimited)
        self.is_active = is_active  # Whether coupon is currently enabled (can be disabled without deleting)
        self.starts_at = starts_at  # When coupon becomes valid (null = valid immediately)
        self.expires_at = expires_at  # When coupon stops working (null = never expires)
        self.created_at = created_at  # When coupon was created
        self.updated_at = updated_at  # When coupon settings were last modified