from sqlalchemy.ext.asyncio import AsyncSession
from Models.CartItem import CartItem


class CartItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = CartItem
