from typing import Any, Optional

class Product:
    """
    Domain model representing a product in the catalog with variants and pricing.
    
    This class manages product information, pricing logic, variant relationships,
    and image associations. It provides caching for performance-critical calculations
    like price ranges and supports multi-variant products.
    
    Key Responsibilities:
        - Store core product information (name, description, pricing)
        - Manage product variants (colors, sizes, etc.)
        - Handle product images with primary image selection
        - Calculate price ranges across variants
        - Provide default variant for simple products
        - Support inventory tracking (SKU, stock quantity)
    
    Design Patterns:
        - Aggregate Root: Owns variants and images
        - Lazy Loading: Variants and images loaded on-demand
        - Caching: Price range cached for performance
    
    Performance Considerations:
        - Price range cached after first calculation
        - Variant/image collections stored in memory
        - Cache invalidated on variant/price changes
    
    Design Notes:
        - Prices stored in cents (avoids floating-point errors)
        - compare_at_price_cents enables strike-through pricing
        - slug used for SEO-friendly URLs
        - This is a domain object; persistence handled by ProductRepository
    """
    def __init__(self, id, name, description, short_description, slug, price_cents, compare_at_price_cents, cost_cents, sku, category_id, is_active, weight, dimensions, created_at, updated_at):
        """
        Initialize a Product domain object.
        
        Args:
            id: Unique identifier (None for new products before persistence)
            name: Product name
            description: Full product description (supports HTML)
            short_description: Brief description for listing pages
            slug: URL-friendly identifier (e.g., 'blue-cotton-shirt')
            price_cents: Current selling price in cents
            compare_at_price_cents: Original price for showing discounts (None if no discount)
            cost_cents: Product cost/COGS in cents
            sku: Stock Keeping Unit identifier
            stock_quantity: Available inventory count
            category_id: Foreign key to product category
            is_active: Whether product is visible to customers
            weight: Product weight (for shipping calculations)
            dimensions: Product dimensions dictionary (for shipping)
            created_at: Product creation timestamp
            updated_at: Last modification timestamp
        """
        self.id = id
        self.name = name
        self.description = description
        self.short_description = short_description
        self.slug = slug
        self.price_cents = price_cents
        self.compare_at_price_cents = compare_at_price_cents
        self.cost_cents = cost_cents
        self.sku = sku
        # self.stock_quantity = stock_quantity  # REMOVED: stock is managed at variant level
        self.category_id = category_id
        self.is_active = is_active
        self.weight = weight
        self.dimensions = dimensions
        self.created_at = created_at
        self.updated_at = updated_at
        self._variants = None
        self._images = None
        self._price_range_cache = None
    
    def get_default_variant(self):
        """
        Get the default variant for this product, prioritizing in-stock variants.
        
        Returns:
            ProductVariant: First in-stock variant, or first variant overall, or None
            
        Selection Logic:
            1. Prefer variants with stock_quantity > 0 (on variants only)
            2. If no in-stock variants, return first variant regardless of stock
            3. If no variants, return None
            
        Design Notes:
            - Used for single-variant products or as fallback
            - Order matters: first in-stock variant wins
            - Assumes variants loaded into self._variants
        """
        if not self._variants:
            return None
        
        active_variants = [v for v in self._variants if getattr(v, 'stock_quantity', 0) > 0]
        
        if not active_variants:
            active_variants = [v for v in self._variants]
        
        return active_variants[0] if active_variants else None
    
    def get_price_range(self) -> dict[str, int]:
        """
        Calculate the min and max prices across all variants.
        
        Returns:
            dict: Contains 'min_cents' and 'max_cents' keys
            
        Caching:
            - Result cached in self._price_range_cache
            - Cache cleared when variants change
            
        Logic:
            - If no variants, returns product's base price
            - Prioritizes in-stock variants for range
            - Falls back to all variants if none in stock
            
        Design Notes:
            - Enables "From $X" pricing display
            - Cache improves performance for product listings
        """
        if self._price_range_cache is not None:
            return self._price_range_cache
        
        if not self._variants:
            self._price_range_cache = {
                "min_cents": self.price_cents,
                "max_cents": self.price_cents
            }
            return self._price_range_cache
        
        active_variant_prices = [
            v.price_cents for v in self._variants 
            if getattr(v, 'stock_quantity', 0) > 0 and hasattr(v, 'price_cents')
        ]
        
        if not active_variant_prices:
            active_variant_prices = [
                v.price_cents for v in self._variants 
                if hasattr(v, 'price_cents')
            ]
        
        if not active_variant_prices:
            self._price_range_cache = {
                "min_cents": self.price_cents,
                "max_cents": self.price_cents
            }
        else:
            self._price_range_cache = {
                "min_cents": min(active_variant_prices),
                "max_cents": max(active_variant_prices)
            }
        
        return self._price_range_cache
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert product to dictionary for API responses.
        
        Returns:
            dict: Product data with computed fields (price_range, discount info,
                  default variant, primary image)
                  
        Includes:
            - Core product fields
            - Price range (min/max across variants)
            - Discount calculation (percentage off)
            - Default variant ID
            - Primary and all image IDs
            - Active/stock status
            
        Design Notes:
            - Images sorted by is_primary flag, then sort_order
            - Discount percentage rounded to integer
            - Suitable for product listing and detail pages
        """
        default_variant = self.get_default_variant()
        price_range = self.get_price_range()
        
        primary_image_id = None
        image_ids = []
        
        if self._images:
            sorted_images = sorted(self._images, key=lambda img: (not getattr(img, 'is_primary', False), getattr(img, 'sort_order', 999)))
            image_ids = [img.id for img in sorted_images if hasattr(img, 'id')]
            
            primary_images = [img for img in sorted_images if getattr(img, 'is_primary', False)]
            if primary_images:
                primary_image_id = primary_images[0].id
            elif image_ids:
                primary_image_id = image_ids[0]
        
        has_discount = self.compare_at_price_cents and self.compare_at_price_cents > self.price_cents
        discount_percentage = None
        if has_discount:
            discount_percentage = int(((self.compare_at_price_cents - self.price_cents) / self.compare_at_price_cents) * 100)
        
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "short_description": self.short_description,
            "price_cents": self.price_cents,
            "compare_at_price_cents": self.compare_at_price_cents,
            "price_range": price_range,
            "sku": self.sku,
            # "stock_quantity": self.stock_quantity,  # REMOVED: stock is managed at variant level
            "is_active": self.is_active,
            "category_id": self.category_id,
            "default_variant_id": default_variant.id if default_variant else None,
            "primary_image_id": primary_image_id,
            "image_ids": image_ids,
            "has_discount": has_discount,
            "discount_percentage": discount_percentage,
            "weight": self.weight,
            "dimensions": self.dimensions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }