"""
wishlist_repository.py

Repository class for managing Wishlist entities in the database.
Provides async operations for retrieving wishlists by ID.
"""

from backend.persistance.wishlist import Wishlist
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class WishlistRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        Args:
            db: SQLAlchemy session or async session.
        """
        self.db = db

    async def get_by_id(self, wishlist_id: int) -> Optional[Wishlist]:
        """
        Retrieve a Wishlist by its ID.
        Args:
            wishlist_id (int): The ID of the wishlist.
        Returns:
            Wishlist or None
        """
        result = await self.db.execute(
            select(Wishlist).filter(Wishlist.wishlist_id == wishlist_id)
        )
        return result.scalars().first()

    async def get_by_user_id(self, user_id: int) -> Optional[Wishlist]:
        """
        Retrieve a Wishlist by the owning user ID.
        Args:
            user_id (int): The ID of the user who owns the wishlist.
        Returns:
            Wishlist or None
        """
        result = await self.db.execute(
            select(Wishlist).filter(Wishlist.user_id == user_id)
        )
        return result.scalars().first()

    async def save(self, wishlist: Wishlist) -> Wishlist:
        """Persist a new wishlist."""
        self.db.add(wishlist)
        await self.db.commit()
        await self.db.refresh(wishlist)
        return wishlist

    async def delete(self, wishlist_id: int) -> bool:
        """Delete a wishlist by ID."""
        wishlist = await self.get_by_id(wishlist_id)
        if not wishlist:
            return False
        await self.db.delete(wishlist)
        await self.db.commit()
        return True
