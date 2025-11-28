from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.ProductOptionCategory import ProductOptionCategory
from typing import List

class ProductOptionCategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = ProductOptionCategory

    async def get_by_id(self, id: int) -> ProductOptionCategory:
        result = await self.db.execute(select(ProductOptionCategory).where(ProductOptionCategory.id == id))
        return result.scalar_one_or_none()

    async def get_by_product(self, product_id: int) -> List[ProductOptionCategory]:
        result = await self.db.execute(select(ProductOptionCategory).where(ProductOptionCategory.product_id == product_id))
        return result.scalars().all()

    async def create(self, poc: ProductOptionCategory) -> ProductOptionCategory:
        self.db.add(poc)
        await self.db.commit()
        await self.db.refresh(poc)
        return poc
