from sqlalchemy.ext.asyncio import AsyncSession
from Models.Order import Order


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Order
