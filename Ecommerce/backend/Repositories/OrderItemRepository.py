from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.OrderItem import OrderItem
from typing import List


class OrderItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = OrderItem
    
    async def get_by_id(self, item_id: int) -> OrderItem:
        result = await self.db.execute(select(OrderItem).where(OrderItem.id == item_id))
        return result.scalar_one_or_none()
    
    async def get_by_order(self, order_id: int) -> List[OrderItem]:
        result = await self.db.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        return result.scalars().all()
    
    async def create(self, order_item: OrderItem) -> OrderItem:
        self.db.add(order_item)
        await self.db.commit()
        await self.db.refresh(order_item)
        return order_item
    
    async def update(self, order_item: OrderItem):
        await self.db.merge(order_item)
        await self.db.commit()
        await self.db.refresh(order_item)
