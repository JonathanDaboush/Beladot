from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.InventoryTransaction import InventoryTransaction
from typing import List


class InventoryTransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = InventoryTransaction
    
    async def create(self, transaction: InventoryTransaction) -> InventoryTransaction:
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction
    
    async def get_by_variant(self, variant_id: int, limit: int = 100) -> List[InventoryTransaction]:
        result = await self.db.execute(
            select(InventoryTransaction)
            .where(InventoryTransaction.variant_id == variant_id)
            .order_by(InventoryTransaction.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_type(self, variant_id: int, transaction_type: str) -> List[InventoryTransaction]:
        result = await self.db.execute(
            select(InventoryTransaction)
            .where(InventoryTransaction.variant_id == variant_id)
            .where(InventoryTransaction.transaction_type == transaction_type)
        )
        return result.scalars().all()
