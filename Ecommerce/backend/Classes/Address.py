# Represents a saved shipping/billing address for a user.
# Users can store multiple addresses and mark one as default for faster checkout.
class Address:
    def __init__(self, id, user_id, address_line1, address_line2, city, state, country, postal_code, is_default):
        self.id = id  # Unique address identifier
        self.user_id = user_id  # Links to User who owns this address
        self.address_line1 = address_line1  # Primary street address (e.g., "123 Main St")
        self.address_line2 = address_line2  # Secondary address details (apartment, suite, building, etc.)
        self.city = city  # City name
        self.state = state  # State/province/region
        self.country = country  # Country (typically 2-letter code like "US", "CA")
        self.postal_code = postal_code  # ZIP/postal code for delivery
        self.is_default = is_default  # Whether this is the user's default shipping address (auto-selected at checkout)