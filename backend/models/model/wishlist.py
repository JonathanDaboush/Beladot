"""
wishlist.py

Model for wishlist entity.
Represents a user's wishlist, including creation and update timestamps.
"""

class Wishlist:
    def __init__(self, wishlist_id, user_id, created_at, updated_at):
        """
        Initialize Wishlist.
        Args:
            wishlist_id (int): Unique identifier for the wishlist.
            user_id (int): Associated user ID.
            created_at (datetime): Creation timestamp.
            updated_at (datetime): Last update timestamp.
        """
        self.wishlist_id = wishlist_id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
