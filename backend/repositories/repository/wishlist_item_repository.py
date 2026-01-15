"""
wishlist_item_repository.py

Repository class for managing WishlistItem entities in the database.
Provides async method for retrieving wishlist items by ID.
"""

from backend.model.wishlist_item import WishlistItem

class WishlistItemRepository:
    def __init__(self, db):
        """
        Initialize the repository with a database session.
        Args:
            db: SQLAlchemy session or async session.
        """
        self.db = db

    async def get_by_id(self, wishlist_item_id):
        """
        Retrieve a wishlist item by its ID.
        Args:
            wishlist_item_id (int): The ID of the wishlist item.
        Returns:
            WishlistItem or None
        """
        return await self.db.query(WishlistItem).filter(WishlistItem.wishlist_item_id == wishlist_item_id).first()
