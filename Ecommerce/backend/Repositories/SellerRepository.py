from Models.Seller import Seller
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class SellerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Seller

    async def create(self, seller: Seller) -> Seller:
        self.db.add(seller)
        await self.db.commit()
        await self.db.refresh(seller)
        return seller

    async def get_by_user_id(self, user_id: int) -> Seller:
        result = await self.db.execute(select(self.model).where(self.model.user_id == user_id))
        return result.scalar_one_or_none()

    async def get(self, seller_id: int) -> Seller:
        result = await self.db.execute(select(self.model).where(self.model.id == seller_id))
        return result.scalar_one_or_none()

    async def list(self) -> list:
        result = await self.db.execute(select(self.model))
        return result.scalars().all()
