





"""
shipment_item_repository.py

Repository class for managing ShipmentItem entities in the database.
Provides async CRUD operations for shipment items.
"""

from backend.model.shipment_item import ShipmentItem
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class ShipmentItemRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, shipment_item_id):
        """
        Retrieve a shipment item by its ID.
        Args:
            shipment_item_id (int): The ID of the shipment item.
        Returns:
            ShipmentItem or None
        """
        result = await self.db.execute(
            select(ShipmentItem).filter(ShipmentItem.shipment_item_id == shipment_item_id)
        )
        return result.scalars().first()

    async def save(self, shipment_item):
        """
        Save a new shipment item to the database.
        Args:
            shipment_item (ShipmentItem): The shipment item to save.
        Returns:
            ShipmentItem: The saved shipment item.
        """
        self.db.add(shipment_item)
        await self.db.commit()
        await self.db.refresh(shipment_item)
        return shipment_item

    async def update(self, shipment_item_id, **kwargs):
        """
        Update a shipment item by ID.
        Args:
            shipment_item_id (int): The ID of the shipment item to update.
            **kwargs: Fields to update.
        Returns:
            ShipmentItem or None: The updated item, or None if not found.
        """
        shipment_item = await self.get_by_id(shipment_item_id)
        if not shipment_item:
            return None
        for k, v in kwargs.items():
            if hasattr(shipment_item, k):
                setattr(shipment_item, k, v)
        await self.db.commit()
        return shipment_item

    async def delete(self, shipment_item_id):
        """
        Delete a shipment item by ID.
        Args:
            shipment_item_id (int): The ID of the shipment item to delete.
        Returns:
            bool: True if deleted, False otherwise.
        """
        shipment_item = await self.get_by_id(shipment_item_id)
        if shipment_item:
            await self.db.delete(shipment_item)
            await self.db.commit()
            return True
        return False
