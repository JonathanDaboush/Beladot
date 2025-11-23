# Represents a product category for organizing and filtering products.
# Categories help customers navigate the store (e.g., "Electronics", "Clothing", "Home & Garden").
class Category:
    def __init__(self, id, name, description, slug, created_at, updated_at):
        self.id = id  # Unique category identifier
        self.name = name  # Display name shown to customers (e.g., "Men's Clothing")
        self.description = description  # Category description for SEO and category pages
        self.slug = slug  # URL-friendly version of name (e.g., "mens-clothing" for /category/mens-clothing)
        self.created_at = created_at  # When category was created
        self.updated_at = updated_at  # When category details were last modified