


"""
return_shipment_repository.py

Repository class for managing ReturnShipment entities in the database.
Provides async method for retrieving return shipments by ID.
"""

from backend.persistance.return_shipment import ReturnShipment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class ReturnShipmentRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, return_shipment_id):
        """
        Retrieve a ReturnShipment by its ID.
        Args:
            return_shipment_id (int): The ID of the return shipment.
        Returns:
            ReturnShipment or None
        """
        result = await self.db.execute(
            select(ReturnShipment).filter(ReturnShipment.return_shipment_id == return_shipment_id)
        )
        return result.scalars().first()
