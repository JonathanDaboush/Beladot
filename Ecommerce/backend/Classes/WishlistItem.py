# Represents a single product saved in a user's wishlist.
# Tracks what products user is interested in for future purchase consideration.
class WishlistItem:
    def __init__(self, id, wishlist_id, variant_id, added_at):
        self.id = id
        self.wishlist_id = wishlist_id
        self.variant_id = variant_id
        self.added_at = added_at
