from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from Models.Cart import Cart
from Models.CartItem import CartItem


class CartRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Cart
    
    async def update(self, cart: Cart):
        await self.db.merge(cart)
        await self.db.commit()
        await self.db.refresh(cart)
    
    async def create_item(self, cart_item: CartItem) -> CartItem:
        self.db.add(cart_item)
        await self.db.commit()
        await self.db.refresh(cart_item)
        return cart_item
    
    async def update_item(self, cart_item: CartItem):
        await self.db.merge(cart_item)
        await self.db.commit()
        await self.db.refresh(cart_item)
    
    async def delete_item(self, cart_item_id: int):
        await self.db.execute(delete(CartItem).where(CartItem.id == cart_item_id))
        await self.db.commit()
