from typing import Any

class OrderItem:
    """
    Domain model representing a single line item in an order (snapshot at purchase time).
    
    This class captures the immutable details of what was purchased, at what price,
    including discounts and taxes. It's a denormalized snapshot to preserve historical
    data even if products change or are deleted.
    
    Key Responsibilities:
        - Store purchased item details (product, variant, quantity, price)
        - Denormalize product/variant names for historical accuracy
        - Track line-level discounts and taxes
        - Calculate final line total
    
    Design Pattern:
        - Snapshot Pattern: Data copied at purchase time, never updated
        - Owned Entity: Lifecycle controlled by Order aggregate
    
    Denormalization Rationale:
        - Product names/SKUs may change after purchase
        - Products may be deleted but orders must remain intact
        - Preserves exactly what customer ordered at that moment
    
    Design Notes:
        - Prices stored in cents (avoids floating-point errors)
        - Line total includes discounts and taxes
        - This is a domain object; persistence handled by OrderItemRepository
    """
    def __init__(self, id, order_id, product_id, variant_id, product_name, product_sku, variant_name, quantity, unit_price_cents, total_price_cents, discount_cents, tax_cents):
        """
        Initialize an OrderItem domain object.
        
        Args:
            id: Unique identifier (None for new items before persistence)
            order_id: Foreign key to parent order
            product_id: Product ID (for reference, not foreign key due to deletion)
            variant_id: Variant ID (for reference, not foreign key due to deletion)
            product_name: Product name snapshot
            product_sku: Product SKU snapshot
            variant_name: Variant name snapshot (e.g., "Blue / Large")
            quantity: Units purchased
            unit_price_cents: Price per unit in cents (after line-level discounts)
            total_price_cents: Line subtotal (quantity × unit_price_cents)
            discount_cents: Line-level discounts applied
            tax_cents: Line-level tax calculated
        """
        self.id = id
        self.order_id = order_id
        self.product_id = product_id
        self.variant_id = variant_id
        self.product_name = product_name
        self.product_sku = product_sku
        self.variant_name = variant_name
        self.quantity = quantity
        self.unit_price_cents = unit_price_cents
        self.total_price_cents = total_price_cents
        self.discount_cents = discount_cents
        self.tax_cents = tax_cents
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert order item to dictionary for API responses.
        
        Returns:
            dict: Order item data with calculated line_total_cents
                  (total - discount + tax)
        """
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "variant_id": self.variant_id,
            "product_name": self.product_name,
            "product_sku": self.product_sku,
            "variant_name": self.variant_name,
            "quantity": self.quantity,
            "unit_price_cents": self.unit_price_cents,
            "total_price_cents": self.total_price_cents,
            "discount_cents": self.discount_cents,
            "tax_cents": self.tax_cents,
            "line_total_cents": self.total_price_cents - self.discount_cents + self.tax_cents
        }