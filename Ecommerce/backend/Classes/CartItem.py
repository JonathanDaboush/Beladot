# Represents a single product in a shopping cart with quantity and pricing.
# Tracks current price at time of adding (prices can change, so we store snapshot for cart display).
class CartItem:
    def __init__(self, id, cart_id, product_id, variant_id, quantity, unit_price_cents, metadata, added_at):
        self.id = id  # Unique cart item identifier
        self.cart_id = cart_id  # Links to parent Cart
        self.product_id = product_id  # Links to Product being added to cart
        self.variant_id = variant_id  # Links to ProductVariant if customer chose size/color (null if no variants)
        self.quantity = quantity  # Number of units customer wants to buy
        self.unit_price_cents = unit_price_cents  # Price per unit when added to cart (snapshot - may differ from current product price)
        self.metadata = metadata  # JSON for custom options or gift messages (e.g., {"engraving": "Happy Birthday"})
        self.added_at = added_at  # When item was added to cart (helps identify abandoned cart age)