from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.ProductVariant import ProductVariant
from Models.InventoryTransaction import InventoryTransaction
from typing import List


class ProductVariantRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = ProductVariant
    
    async def get_by_id(self, variant_id: int) -> ProductVariant:
        result = await self.db.execute(select(ProductVariant).where(ProductVariant.id == variant_id))
        return result.scalar_one_or_none()
    
    async def update(self, variant: ProductVariant):
        await self.db.merge(variant)
        await self.db.commit()
        await self.db.refresh(variant)
    
    async def create_transaction(self, transaction: InventoryTransaction) -> InventoryTransaction:
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction
    
    async def get_active_reservations(self, variant_id: int) -> List[InventoryTransaction]:
        result = await self.db.execute(
            select(InventoryTransaction)
            .where(InventoryTransaction.variant_id == variant_id)
            .where(InventoryTransaction.transaction_type == 'reservation')
        )
        return result.scalars().all()
