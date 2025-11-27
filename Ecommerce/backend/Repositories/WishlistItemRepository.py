from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.WishlistItem import WishlistItem
from typing import List


class WishlistItemRepository:
    """
    Data access layer for WishlistItem entities.
    
    This repository manages wishlist item persistence, supporting
    individual item operations and wishlist-level item queries.
    
    Responsibilities:
        - WishlistItem CRUD operations
        - Query items by wishlist
        - Support wishlist management
    
    Design Patterns:
        - Repository Pattern: Isolates wishlist item data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = WishlistItemRepository(db_session)
        items = await repository.get_by_wishlist(wishlist_id)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = WishlistItem
    
    async def get_by_id(self, item_id: int) -> WishlistItem:
        """
        Retrieve a wishlist item by ID.
        
        Args:
            item_id: The unique ID of the wishlist item
            
        Returns:
            WishlistItem: The item if found, None otherwise
        """
        result = await self.db.execute(select(WishlistItem).where(WishlistItem.id == item_id))
        return result.scalar_one_or_none()
    
    async def get_by_wishlist(self, wishlist_id: int) -> List[WishlistItem]:
        """
        Retrieve all items in a wishlist.
        
        Args:
            wishlist_id: The wishlist ID
            
        Returns:
            List[WishlistItem]: All items in the wishlist
        """
        result = await self.db.execute(
            select(WishlistItem).where(WishlistItem.wishlist_id == wishlist_id)
        )
        return result.scalars().all()
    
    async def create(self, wishlist_item: WishlistItem) -> WishlistItem:
        """
        Add an item to a wishlist.
        
        Args:
            wishlist_item: WishlistItem to add
            
        Returns:
            WishlistItem: Created item with database-generated ID
            
        Side Effects:
            Commits transaction immediately
        """
        self.db.add(wishlist_item)
        await self.db.commit()
        await self.db.refresh(wishlist_item)
        return wishlist_item
    
    async def update(self, wishlist_item: WishlistItem):
        """
        Update a wishlist item.
        
        Args:
            wishlist_item: WishlistItem with modifications
            
        Side Effects:
            Commits transaction immediately
        """
        await self.db.merge(wishlist_item)
        await self.db.commit()
        await self.db.refresh(wishlist_item)
    
    async def delete(self, item_id: int):
        """
        Remove an item from a wishlist.
        
        Args:
            item_id: The wishlist item ID to delete
            
        Side Effects:
            Deletes item if exists
            Commits transaction immediately
        """
        item = await self.get_by_id(item_id)
        if item:
            await self.db.delete(item)
            await self.db.commit()
