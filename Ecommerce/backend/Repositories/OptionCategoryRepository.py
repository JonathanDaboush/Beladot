from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.OptionCategory import OptionCategory
from typing import List

class OptionCategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = OptionCategory

    async def get_by_id(self, category_id: int) -> OptionCategory:
        result = await self.db.execute(select(OptionCategory).where(OptionCategory.id == category_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> List[OptionCategory]:
        result = await self.db.execute(select(OptionCategory))
        return result.scalars().all()

    async def create(self, category: OptionCategory) -> OptionCategory:
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category
