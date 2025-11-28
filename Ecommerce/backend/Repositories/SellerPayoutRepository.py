from Models.SellerPayout import SellerPayout
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

class SellerPayoutRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = SellerPayout

    async def create(self, payout: SellerPayout) -> SellerPayout:
        self.db.add(payout)
        await self.db.commit()
        await self.db.refresh(payout)
        return payout

    async def get_by_seller(self, seller_id: int) -> List[SellerPayout]:
        result = await self.db.execute(select(SellerPayout).where(SellerPayout.seller_id == seller_id))
        return result.scalars().all()

    async def get_between_dates(self, seller_id: int, start_date, end_date) -> List[SellerPayout]:
        result = await self.db.execute(
            select(SellerPayout).where(
                SellerPayout.seller_id == seller_id,
                SellerPayout.payout_date >= start_date,
                SellerPayout.payout_date <= end_date
            )
        )
        return result.scalars().all()
