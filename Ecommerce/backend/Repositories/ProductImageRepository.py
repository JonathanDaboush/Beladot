from sqlalchemy.ext.asyncio import AsyncSession
from Models.ProductImage import ProductImage


class ProductImageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = ProductImage
