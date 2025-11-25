from typing import Any

class OrderItem:
    def __init__(self, id, order_id, product_id, variant_id, product_name, product_sku, variant_name, quantity, unit_price_cents, total_price_cents, discount_cents, tax_cents):
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