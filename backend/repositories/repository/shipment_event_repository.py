





"""
shipment_event_repository.py

Repository class for managing ShipmentEvent entities in the database.
Provides async CRUD operations for shipment events.
"""

from backend.model.shipment_event import ShipmentEvent
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class ShipmentEventRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, event_id):
        """
        Retrieve a shipment event by its ID.
        Args:
            event_id (int): The ID of the shipment event.
        Returns:
            ShipmentEvent or None
        """
        result = await self.db.execute(
            select(ShipmentEvent).filter(ShipmentEvent.event_id == event_id)
        )
        return result.scalars().first()

    async def save(self, shipment_event):
        """
        Save a new shipment event to the database.
        Args:
            shipment_event (ShipmentEvent): The shipment event to save.
        Returns:
            ShipmentEvent: The saved shipment event.
        """
        self.db.add(shipment_event)
        await self.db.commit()
        await self.db.refresh(shipment_event)
        return shipment_event

    async def update(self, event_id, **kwargs):
        """
        Update a shipment event by ID.
        Args:
            event_id (int): The ID of the shipment event to update.
            **kwargs: Fields to update.
        Returns:
            ShipmentEvent or None: The updated event, or None if not found.
        """
        shipment_event = await self.get_by_id(event_id)
        if not shipment_event:
            return None
        for k, v in kwargs.items():
            if hasattr(shipment_event, k):
                setattr(shipment_event, k, v)
        await self.db.commit()
        return shipment_event

    async def delete(self, event_id):
        """
        Delete a shipment event by ID.
        Args:
            event_id (int): The ID of the shipment event to delete.
        Returns:
            bool: True if deleted, False otherwise.
        """
        shipment_event = await self.get_by_id(event_id)
        if shipment_event:
            await self.db.delete(shipment_event)
            await self.db.commit()
            return True
        return False
