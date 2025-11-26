from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from Models.Wishlist import Wishlist
from Models.WishlistItem import WishlistItem


class WishlistRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Wishlist
    
    async def update(self, wishlist: Wishlist):
        await self.db.merge(wishlist)
        await self.db.commit()
        await self.db.refresh(wishlist)
    
    async def create_item(self, wishlist_item: WishlistItem) -> WishlistItem:
        self.db.add(wishlist_item)
        await self.db.commit()
        await self.db.refresh(wishlist_item)
        return wishlist_item
    
    async def delete_item_by_variant(self, wishlist_id: int, variant_id: int):
        await self.db.execute(
            delete(WishlistItem)
            .where(WishlistItem.wishlist_id == wishlist_id)
            .where(WishlistItem.variant_id == variant_id)
        )
        await self.db.commit()
