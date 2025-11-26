from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.CartItem import CartItem
from typing import List


class CartItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = CartItem
    
    async def get_by_id(self, item_id: int) -> CartItem:
        result = await self.db.execute(select(CartItem).where(CartItem.id == item_id))
        return result.scalar_one_or_none()
    
    async def get_by_cart(self, cart_id: int) -> List[CartItem]:
        result = await self.db.execute(
            select(CartItem).where(CartItem.cart_id == cart_id)
        )
        return result.scalars().all()
    
    async def create(self, cart_item: CartItem) -> CartItem:
        self.db.add(cart_item)
        await self.db.commit()
        await self.db.refresh(cart_item)
        return cart_item
    
    async def update(self, cart_item: CartItem):
        await self.db.merge(cart_item)
        await self.db.commit()
        await self.db.refresh(cart_item)
    
    async def delete(self, item_id: int):
        item = await self.get_by_id(item_id)
        if item:
            await self.db.delete(item)
            await self.db.commit()
