from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.ShipmentItem import ShipmentItem
from typing import List


class ShipmentItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = ShipmentItem
    
    async def get_by_id(self, item_id: int) -> ShipmentItem:
        result = await self.db.execute(select(ShipmentItem).where(ShipmentItem.id == item_id))
        return result.scalar_one_or_none()
    
    async def get_by_shipment(self, shipment_id: int) -> List[ShipmentItem]:
        result = await self.db.execute(
            select(ShipmentItem).where(ShipmentItem.shipment_id == shipment_id)
        )
        return result.scalars().all()
    
    async def create(self, shipment_item: ShipmentItem) -> ShipmentItem:
        self.db.add(shipment_item)
        await self.db.commit()
        await self.db.refresh(shipment_item)
        return shipment_item
    
    async def update(self, shipment_item: ShipmentItem):
        await self.db.merge(shipment_item)
        await self.db.commit()
        await self.db.refresh(shipment_item)
