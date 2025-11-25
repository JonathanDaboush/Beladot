from sqlalchemy.ext.asyncio import AsyncSession
from Models.Coupon import Coupon


class CouponRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Coupon
