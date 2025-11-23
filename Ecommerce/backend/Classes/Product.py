# Represents a product available for sale in the e-commerce store.
# Tracks pricing (what you sell for vs what you paid), inventory, physical attributes, and product visibility.
class Product:
    def __init__(self, id, name, description, slug, price_cents, compare_at_price_cents, cost_cents, sku, stock_quantity, category_id, is_active, weight, dimensions, created_at, updated_at):
        self.id = id  # Unique product identifier in database
        self.name = name  # Product display name shown to customers (e.g., "Men's Cotton T-Shirt")
        self.description = description  # Detailed product information, features, and materials for product pages
        self.slug = slug  # URL-friendly version of name for clean links (e.g., "mens-cotton-t-shirt" from "Men's Cotton T-Shirt")
        self.price_cents = price_cents  # Customer-facing sale price in cents (what you charge and profit from)
        self.compare_at_price_cents = compare_at_price_cents  # Original/MSRP price shown crossed-out to display savings (e.g., was $50, now $40)
        self.cost_cents = cost_cents  # What you paid supplier/manufacturer per unit (for profit margin calculation)
        self.sku = sku  # Stock Keeping Unit - unique tracking code for inventory management (e.g., "TSH-BLU-M-001")
        self.stock_quantity = stock_quantity  # Number of units currently available in inventory
        self.category_id = category_id  # Links to Category for product organization and filtering
        self.is_active = is_active  # Whether product is visible on storefront (false = hidden/discontinued but not deleted)
        self.weight = weight  # Product weight in grams/ounces for shipping cost calculation
        self.dimensions = dimensions  # Package dimensions as JSON (e.g., {"length": 10, "width": 8, "height": 2}) for shipping
        self.created_at = created_at  # When product was added to catalog
        self.updated_at = updated_at  # When product details were last modified