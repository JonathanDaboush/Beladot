from sqlalchemy.ext.asyncio import AsyncSession
from Models.Address import Address


class AddressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Address
