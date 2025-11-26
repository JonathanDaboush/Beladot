from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.WishlistItem import WishlistItem
from typing import List


class WishlistItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = WishlistItem
    
    async def get_by_id(self, item_id: int) -> WishlistItem:
        result = await self.db.execute(select(WishlistItem).where(WishlistItem.id == item_id))
        return result.scalar_one_or_none()
    
    async def get_by_wishlist(self, wishlist_id: int) -> List[WishlistItem]:
        result = await self.db.execute(
            select(WishlistItem).where(WishlistItem.wishlist_id == wishlist_id)
        )
        return result.scalars().all()
    
    async def create(self, wishlist_item: WishlistItem) -> WishlistItem:
        self.db.add(wishlist_item)
        await self.db.commit()
        await self.db.refresh(wishlist_item)
        return wishlist_item
    
    async def update(self, wishlist_item: WishlistItem):
        await self.db.merge(wishlist_item)
        await self.db.commit()
        await self.db.refresh(wishlist_item)
    
    async def delete(self, item_id: int):
        item = await self.get_by_id(item_id)
        if item:
            await self.db.delete(item)
            await self.db.commit()
