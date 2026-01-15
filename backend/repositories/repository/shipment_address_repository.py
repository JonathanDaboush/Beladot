"""
shipment_address_repository.py

Repository class for managing ShipmentAddress entities in the database.
Provides async method for retrieving shipment addresses by ID.
"""

from backend.model.shipment_address import ShipmentAddress
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class ShipmentAddressRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, shipment_address_id):
        """
        Retrieve a shipment address by its ID.
        Args:
            shipment_address_id (int): The ID of the shipment address.
        Returns:
            ShipmentAddress or None
        """
        result = await self.db.execute(
            select(ShipmentAddress).filter(ShipmentAddress.shipment_address_id == shipment_address_id)
        )
        return result.scalars().first()
