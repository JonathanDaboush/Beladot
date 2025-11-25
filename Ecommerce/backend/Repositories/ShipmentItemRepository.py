from sqlalchemy.ext.asyncio import AsyncSession
from Models.ShipmentItem import ShipmentItem


class ShipmentItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = ShipmentItem
