from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Refund import Refund
from typing import List


class RefundRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Refund
    
    async def get_by_id(self, refund_id: int) -> Refund:
        result = await self.db.execute(select(Refund).where(Refund.id == refund_id))
        return result.scalar_one_or_none()
    
    async def get_by_order(self, order_id: int) -> List[Refund]:
        result = await self.db.execute(
            select(Refund).where(Refund.order_id == order_id)
        )
        return result.scalars().all()
    
    async def create(self, refund: Refund) -> Refund:
        self.db.add(refund)
        await self.db.commit()
        await self.db.refresh(refund)
        return refund
    
    async def update(self, refund: Refund):
        await self.db.merge(refund)
        await self.db.commit()
        await self.db.refresh(refund)
