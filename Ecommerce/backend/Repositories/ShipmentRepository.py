from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Shipment import Shipment


class ShipmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Shipment
    
    async def update(self, shipment: Shipment):
        await self.db.merge(shipment)
        await self.db.commit()
        await self.db.refresh(shipment)
