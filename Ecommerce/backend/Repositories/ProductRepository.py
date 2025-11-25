from sqlalchemy.ext.asyncio import AsyncSession
from Models.Product import Product


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Product
