"""
wishlist_repository.py

Repository class for managing Wishlist entities in the database.
Provides async operations for retrieving wishlists by ID.
"""

from backend.model.wishlist import Wishlist

class WishlistRepository:
    def __init__(self, db):
        """
        Initialize the repository with a database session.
        Args:
            db: SQLAlchemy session or async session.
        """
        self.db = db

    async def get_by_id(self, wishlist_id):
        """
        Retrieve a Wishlist by its ID.
        Args:
            wishlist_id (int): The ID of the wishlist.
        Returns:
            Wishlist or None
        """
        return await self.db.query(Wishlist).filter(Wishlist.wishlist_id == wishlist_id).first()
