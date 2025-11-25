from sqlalchemy.ext.asyncio import AsyncSession
from Models.Shipment import Shipment


class ShipmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Shipment
