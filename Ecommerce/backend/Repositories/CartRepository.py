from sqlalchemy.ext.asyncio import AsyncSession
from Models.Cart import Cart


class CartRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Cart
