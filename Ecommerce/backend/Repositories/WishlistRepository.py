from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from Models.Wishlist import Wishlist
from Models.WishlistItem import WishlistItem


class WishlistRepository:
    """
    Data access layer for Wishlist and WishlistItem entities.
    
    This repository manages user wishlists (saved items), supporting
    wishlist updates and item management (add/remove).
    
    Responsibilities:
        - Wishlist updates (timestamps)
        - WishlistItem creation and deletion
        - Support saved items management
    
    Design Patterns:
        - Aggregate Root: Wishlist owns WishlistItems
        - Repository Pattern: Unified wishlist data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = WishlistRepository(db_session)
        await repository.update(wishlist)
        item = await repository.create_item(wishlist_item)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = Wishlist
    
    async def update(self, wishlist: Wishlist):
        """
        Update wishlist (typically just timestamps).
        
        Args:
            wishlist: Wishlist object with modifications
            
        Side Effects:
            Updates updated_at timestamp
            Commits transaction immediately
        """
        await self.db.merge(wishlist)
        await self.db.commit()
        await self.db.refresh(wishlist)
    
    async def create_item(self, wishlist_item: WishlistItem) -> WishlistItem:
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
    
    async def delete_item_by_variant(self, wishlist_id: int, variant_id: int):
        """
        Remove a specific variant from a wishlist.
        
        Args:
            wishlist_id: The wishlist ID
            variant_id: The product variant to remove
            
        Side Effects:
            Deletes matching wishlist item(s)
            Commits transaction immediately
        """
        await self.db.execute(
            delete(WishlistItem)
            .where(WishlistItem.wishlist_id == wishlist_id)
            .where(WishlistItem.variant_id == variant_id)
        )
        await self.db.commit()
