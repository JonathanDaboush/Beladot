from sqlalchemy.ext.asyncio import AsyncSession
from Models.ProductVariant import ProductVariant


class ProductVariantRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = ProductVariant
