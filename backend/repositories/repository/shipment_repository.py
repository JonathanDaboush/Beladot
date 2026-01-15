





"""
shipment_repository.py

Repository class for managing Shipment entities in the database.
Provides async CRUD operations for shipments.
"""

from backend.persistance.shipment import Shipment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class ShipmentRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, shipment_id):
        """
        Retrieve a shipment by its ID.
        Args:
            shipment_id (int): The ID of the shipment.
        Returns:
            Shipment or None
        """
        result = await self.db.execute(
            select(Shipment).filter(Shipment.shipment_id == shipment_id)
        )
        return result.scalars().first()

    async def save(self, shipment):
        """
        Save a new shipment to the database.
        Args:
            shipment (Shipment): The shipment to save.
        Returns:
            Shipment: The saved shipment.
        """
        self.db.add(shipment)
        await self.db.commit()
        await self.db.refresh(shipment)
        return shipment

    async def update(self, shipment_id, **kwargs):
        """
        Update a shipment by ID.
        Args:
            shipment_id (int): The ID of the shipment to update.
            **kwargs: Fields to update.
        Returns:
            Shipment or None: The updated shipment, or None if not found.
        """
        shipment = await self.get_by_id(shipment_id)
        if not shipment:
            return None
        for k, v in kwargs.items():
            if hasattr(shipment, k):
                setattr(shipment, k, v)
        await self.db.commit()
        return shipment

    async def delete(self, shipment_id):
        """
        Delete a shipment by ID.
        Args:
            shipment_id (int): The ID of the shipment to delete.
        Returns:
            bool: True if deleted, False otherwise.
        """
        shipment = await self.get_by_id(shipment_id)
        if shipment:
            await self.db.delete(shipment)
            await self.db.commit()
            return True
        return False
