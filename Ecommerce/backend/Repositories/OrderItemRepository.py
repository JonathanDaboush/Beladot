from sqlalchemy.ext.asyncio import AsyncSession
from Models.OrderItem import OrderItem


class OrderItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = OrderItem
