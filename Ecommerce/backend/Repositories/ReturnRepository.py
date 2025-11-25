from sqlalchemy.ext.asyncio import AsyncSession
from Models.Return import Return


class ReturnRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Return
