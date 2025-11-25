from typing import Any

class CartItem:
    def __init__(self, id, cart_id, product_id, variant_id, quantity, unit_price_cents, item_metadata, added_at):
        self.id = id
        self.cart_id = cart_id
        self.product_id = product_id
        self.variant_id = variant_id
        self.quantity = quantity
        self.unit_price_cents = unit_price_cents
        self.item_metadata = item_metadata
        self.added_at = added_at
    
    def line_total_cents(self) -> int:
        return self.quantity * self.unit_price_cents
    
    def to_dict(self) -> dict[str, Any]:
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