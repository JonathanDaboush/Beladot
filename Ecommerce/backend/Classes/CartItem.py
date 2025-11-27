from typing import Any

class CartItem:
    """
    Domain model representing a single line item in a shopping cart.
    
    This class represents one product variant with quantity and pricing in a cart.
    It's owned by the Cart aggregate and handles line total calculations.
    
    Key Responsibilities:
        - Store product variant selection (variant_id, product_id)
        - Track quantity and unit price
        - Calculate line total (quantity × unit price)
        - Support custom metadata (engraving, gift messages, etc.)
        - Track when item was added to cart
    
    Design Patterns:
        - Value Object within Cart aggregate
        - Owned entity (lifecycle controlled by Cart)
    
    Design Notes:
        - Price stored at cart time (price lock)
        - Metadata enables customization without schema changes
        - This is a domain object; persistence handled by CartItemRepository
    """
    def __init__(self, id, cart_id, product_id, variant_id, quantity, unit_price_cents, item_metadata, added_at):
        """
        Initialize a CartItem domain object.
        
        Args:
            id: Unique identifier (None for new items before persistence)
            cart_id: Foreign key to the parent cart
            product_id: Parent product identifier
            variant_id: Specific product variant identifier
            quantity: Number of units
            unit_price_cents: Price per unit in cents (locked at add time)
            item_metadata: Custom data dictionary (e.g., {'engraving': 'John'})
            added_at: Timestamp when added to cart
        """
        self.id = id
        self.cart_id = cart_id
        self.product_id = product_id
        self.variant_id = variant_id
        self.quantity = quantity
        self.unit_price_cents = unit_price_cents
        self.item_metadata = item_metadata
        self.added_at = added_at
    
    def line_total_cents(self) -> int:
        """
        Calculate the total price for this line item.
        
        Returns:
            int: Total in cents (quantity × unit_price_cents)
        """
        return self.quantity * self.unit_price_cents
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert cart item to dictionary for API responses.
        
        Returns:
            dict: Cart item data with id, cart_id, product_id, variant_id,
                  quantity, unit_price_cents, line_total_cents, metadata, added_at
        """
        return {
            "id": self.id,
            "cart_id": self.cart_id,
            "product_id": self.product_id,
            "variant_id": self.variant_id,
            "quantity": self.quantity,
            "unit_price_cents": self.unit_price_cents,
            "line_total_cents": self.line_total_cents(),
            "metadata": self.item_metadata,
            "added_at": self.added_at.isoformat() if self.added_at else None
        }