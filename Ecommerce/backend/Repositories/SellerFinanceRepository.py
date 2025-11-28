from Models.SellerFinance import SellerFinance
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class SellerFinanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = SellerFinance

    async def create(self, finance: SellerFinance) -> SellerFinance:
        self.db.add(finance)
        await self.db.commit()
        await self.db.refresh(finance)
        return finance

    async def get_by_seller_id(self, seller_id: int) -> SellerFinance:
        result = await self.db.execute(select(self.model).where(self.model.seller_id == seller_id))
        return result.scalar_one_or_none()

    async def get(self, finance_id: int) -> SellerFinance:
        result = await self.db.execute(select(self.model).where(self.model.id == finance_id))
        return result.scalar_one_or_none()
