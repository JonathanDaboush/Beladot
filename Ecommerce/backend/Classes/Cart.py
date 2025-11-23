# Represents a shopping cart that holds products before checkout.
# A cart contains multiple CartItems. Logged-in users have persistent carts; guests have session-based carts.
class Cart:
    def __init__(self, id, user_id, created_at, updated_at):
        self.id = id  # Unique cart identifier
        self.user_id = user_id  # Links to User who owns the cart (null for guest/anonymous carts)
        self.created_at = created_at  # When the cart was first created
        self.updated_at = updated_at  # When items were last added/removed or quantities changed