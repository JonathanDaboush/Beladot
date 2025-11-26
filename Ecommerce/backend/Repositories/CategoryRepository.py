from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Category import Category


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Category
    
    async def get_by_id(self, category_id: int) -> Category:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()
    
    async def update(self, category: Category):
        await self.db.merge(category)
        await self.db.commit()
        await self.db.refresh(category)
