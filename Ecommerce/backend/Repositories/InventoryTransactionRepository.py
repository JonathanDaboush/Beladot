from sqlalchemy.ext.asyncio import AsyncSession
from Models.InventoryTransaction import InventoryTransaction


class InventoryTransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = InventoryTransaction
