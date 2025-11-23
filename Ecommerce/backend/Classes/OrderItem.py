# Represents a single line item in an order - captures product snapshot at time of purchase.
# Stores product details like name/SKU to preserve historical record even if product is later deleted or modified.
class OrderItem:
    def __init__(self, id, order_id, product_id, variant_id, product_name, product_sku, variant_name, quantity, unit_price_cents, total_price_cents, discount_cents, tax_cents):
        self.id = id  # Unique line item identifier
        self.order_id = order_id  # Links to parent Order
        self.product_id = product_id  # Reference to Product for reporting (may be null if product deleted)
        self.variant_id = variant_id  # Reference to ProductVariant if customer chose size/color (null for products without variants)
        self.product_name = product_name  # Product name at time of purchase (snapshot for historical record)
        self.product_sku = product_sku  # Product SKU at time of purchase (for fulfillment and inventory tracking) BARCODE!
        self.variant_name = variant_name  # Variant details like "Size: Large, Color: Blue" (null if no variant)
        self.quantity = quantity  # Number of units customer ordered (e.g., 2 shirts)
        self.unit_price_cents = unit_price_cents  # Price per single unit at time of purchase (in cents)
        self.total_price_cents = total_price_cents  # quantity × unit_price_cents before discounts (in cents)
        self.discount_cents = discount_cents  # Per-item discount applied (e.g., from bulk discount or sale price) in cents
        self.tax_cents = tax_cents  # Tax calculated for this line item based on quantity and location (in cents)
