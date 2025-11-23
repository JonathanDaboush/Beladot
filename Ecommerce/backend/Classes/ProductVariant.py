# Represents different versions/options of a single product (e.g., T-shirt in different sizes/colors)
# Each variant has its own SKU, price, and inventory separate from the base product
class ProductVariant:
    def __init__(self, id, product_id, sku, name, price_cents, compare_at_price_cents, cost_cents, stock_quantity, inventory_management, inventory_policy, track_stock, option1_name, option1_value, option2_name, option2_value, option3_name, option3_value):
        self.id = id  # Unique identifier for this variant
        self.product_id = product_id  # Reference to the parent product
        self.sku = sku  # Unique SKU for this specific variant (e.g., "TSHIRT-BLK-M")
        self.name = name  # Display name for this variant (e.g., "Black / Medium")
        self.price_cents = price_cents  # Selling price in cents (can differ from base product)
        self.compare_at_price_cents = compare_at_price_cents  # Original price for showing discounts
        self.cost_cents = cost_cents  # Your cost for this variant
        self.stock_quantity = stock_quantity  # How many units in stock for this variant
        self.inventory_management = inventory_management  # System managing inventory (e.g., "shopify", "manual")
        self.inventory_policy = inventory_policy  # "deny" (prevent overselling) or "continue" (allow backorders)
        self.track_stock = track_stock  # Whether to track inventory for this variant
        self.option1_name = option1_name  # First option type (e.g., "Size")
        self.option1_value = option1_value  # First option value (e.g., "Medium")
        self.option2_name = option2_name  # Second option type (e.g., "Color")
        self.option2_value = option2_value  # Second option value (e.g., "Black")
        self.option3_name = option3_name  # Third option type (e.g., "Material")
        self.option3_value = option3_value  # Third option value (e.g., "Cotton")