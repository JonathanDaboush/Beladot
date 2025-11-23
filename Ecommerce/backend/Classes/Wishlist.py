# Represents a user's saved list of products they're interested in for future purchase.
# Wishlists help users bookmark items and can be used for gift registries or purchase reminders.
class Wishlist:
    def __init__(self, id, user_id, created_at, updated_at):
        self.id = id  # Unique wishlist identifier
        self.user_id = user_id  # Links to User who owns this wishlist
        self.created_at = created_at  # When wishlist was created (typically when user adds first item)
        self.updated_at = updated_at  # When items were last added/removed from wishlist
