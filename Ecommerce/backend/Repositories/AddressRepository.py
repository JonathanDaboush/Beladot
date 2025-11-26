from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Address import Address
from typing import List


class AddressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Address
    
    async def get_by_id(self, address_id: int) -> Address:
        result = await self.db.execute(select(Address).where(Address.id == address_id))
        return result.scalar_one_or_none()
    
    async def get_by_user(self, user_id: int) -> List[Address]:
        result = await self.db.execute(
            select(Address).where(Address.user_id == user_id)
        )
        return result.scalars().all()
    
    async def create(self, address: Address) -> Address:
        self.db.add(address)
        await self.db.commit()
        await self.db.refresh(address)
        return address
    
    async def update(self, address: Address):
        await self.db.merge(address)
        await self.db.commit()
        await self.db.refresh(address)
    
    async def delete(self, address_id: int):
        address = await self.get_by_id(address_id)
        if address:
            await self.db.delete(address)
            await self.db.commit()
