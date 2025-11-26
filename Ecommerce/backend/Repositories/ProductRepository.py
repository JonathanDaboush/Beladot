from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Product import Product
from typing import List


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Product
    
    async def get_by_id(self, product_id: int) -> Product:
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug: str) -> Product:
        result = await self.db.execute(select(Product).where(Product.slug == slug))
        return result.scalar_one_or_none()
    
    async def create(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product
    
    async def update(self, product: Product):
        await self.db.merge(product)
        await self.db.commit()
        await self.db.refresh(product)
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Product]:
        result = await self.db.execute(
            select(Product).limit(limit).offset(offset)
        )
        return result.scalars().all()
