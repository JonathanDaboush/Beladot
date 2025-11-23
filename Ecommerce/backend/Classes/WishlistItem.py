# Represents a single product saved in a user's wishlist.
# Tracks what products user is interested in for future purchase consideration.
class WishlistItem:
    def __init__(self, id, wishlist_id, product_id, added_at):
        self.id = id  # Unique wishlist item identifier
        self.wishlist_id = wishlist_id  # Links to parent Wishlist
        self.product_id = product_id  # Links to Product user wants to save
        self.added_at = added_at  # When product was added to wishlist (helps track interest over time)
