from typing import Any, Optional

class Product:
    def __init__(self, id, name, description, short_description, slug, price_cents, compare_at_price_cents, cost_cents, sku, stock_quantity, category_id, is_active, weight, dimensions, created_at, updated_at):
        self.id = id
        self.name = name
        self.description = description
        self.short_description = short_description
        self.slug = slug
        self.price_cents = price_cents
        self.compare_at_price_cents = compare_at_price_cents
        self.cost_cents = cost_cents
        self.sku = sku
        self.stock_quantity = stock_quantity
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
        if not self._variants:
            return None
        
        active_variants = [v for v in self._variants if getattr(v, 'stock_quantity', 0) > 0]
        
        if not active_variants:
            active_variants = [v for v in self._variants]
        
        return active_variants[0] if active_variants else None
    
    def get_price_range(self) -> dict[str, int]:
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
            "stock_quantity": self.stock_quantity,
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