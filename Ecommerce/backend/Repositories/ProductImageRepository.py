from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.ProductImage import ProductImage
from typing import List


class ProductImageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = ProductImage
    
    async def get_by_id(self, image_id: int) -> ProductImage:
        result = await self.db.execute(select(ProductImage).where(ProductImage.id == image_id))
        return result.scalar_one_or_none()
    
    async def get_by_product(self, product_id: int) -> List[ProductImage]:
        result = await self.db.execute(
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.sort_order)
        )
        return result.scalars().all()
    
    async def create(self, image: ProductImage) -> ProductImage:
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)
        return image
    
    async def update(self, image: ProductImage):
        await self.db.merge(image)
        await self.db.commit()
        await self.db.refresh(image)
    
    async def delete(self, image_id: int):
        image = await self.get_by_id(image_id)
        if image:
            await self.db.delete(image)
            await self.db.commit()
