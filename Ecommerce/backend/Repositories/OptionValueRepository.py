from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.OptionValue import OptionValue
from typing import List

class OptionValueRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = OptionValue

    async def get_by_id(self, value_id: int) -> OptionValue:
        result = await self.db.execute(select(OptionValue).where(OptionValue.id == value_id))
        return result.scalar_one_or_none()

    async def get_by_category(self, category_id: int) -> List[OptionValue]:
        result = await self.db.execute(select(OptionValue).where(OptionValue.category_id == category_id))
        return result.scalars().all()

    async def create(self, value: OptionValue) -> OptionValue:
        self.db.add(value)
        await self.db.commit()
        await self.db.refresh(value)
        return value
