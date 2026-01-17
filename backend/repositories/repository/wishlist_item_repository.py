"""
wishlist_item_repository.py

Repository class for managing WishlistItem entities in the database.
Provides async method for retrieving wishlist items by ID.
"""

from typing import Optional
from backend.persistance.wishlist_item import WishlistItem
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class WishlistItemRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, wishlist_item_id: int) -> Optional[WishlistItem]:
        """
        Retrieve a wishlist item by its ID.
        Args:
            wishlist_item_id (int): The ID of the wishlist item.
        Returns:
            WishlistItem or None
        """
        result = await self.db.execute(
            select(WishlistItem).filter(WishlistItem.wishlist_item_id == wishlist_item_id)
        )
        return result.scalars().first()
