from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.ProductOptionValue import ProductOptionValue
from typing import List

class ProductOptionValueRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = ProductOptionValue

    async def get_by_id(self, id: int) -> ProductOptionValue:
        result = await self.db.execute(select(ProductOptionValue).where(ProductOptionValue.id == id))
        return result.scalar_one_or_none()

    async def get_by_product(self, product_id: int) -> List[ProductOptionValue]:
        result = await self.db.execute(select(ProductOptionValue).where(ProductOptionValue.product_id == product_id))
        return result.scalars().all()

    async def create(self, pov: ProductOptionValue) -> ProductOptionValue:
        self.db.add(pov)
        await self.db.commit()
        await self.db.refresh(pov)
        return pov
