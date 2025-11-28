from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.CouponEligibility import CouponEligibility
from typing import List

class CouponEligibilityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = CouponEligibility

    async def get_by_id(self, id: int) -> CouponEligibility:
        result = await self.db.execute(select(CouponEligibility).where(CouponEligibility.id == id))
        return result.scalar_one_or_none()

    async def get_by_coupon(self, coupon_id: int) -> List[CouponEligibility]:
        result = await self.db.execute(select(CouponEligibility).where(CouponEligibility.coupon_id == coupon_id))
        return result.scalars().all()

    async def create(self, eligibility: CouponEligibility) -> CouponEligibility:
        self.db.add(eligibility)
        await self.db.commit()
        await self.db.refresh(eligibility)
        return eligibility
