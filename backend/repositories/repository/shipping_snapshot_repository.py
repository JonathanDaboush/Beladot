




"""
shipping_snapshot_repository.py

Repository class for managing ShippingSnapshot entities in the database.
Provides async CRUD operations for shipping snapshots.
"""

from backend.persistance.shipping_snapshot import ShippingSnapshot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class ShippingSnapshotRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, snapshot_id):
        """
        Retrieve a shipping snapshot by its ID.
        Args:
            snapshot_id (int): The ID of the shipping snapshot.
        Returns:
            ShippingSnapshot or None
        """
        result = await self.db.execute(
            select(ShippingSnapshot).filter(ShippingSnapshot.snapshot_id == snapshot_id)
        )
        return result.scalars().first()

    async def save(self, snapshot):
        """
        Save a new shipping snapshot to the database.
        Args:
            snapshot (ShippingSnapshot): The shipping snapshot to save.
        Returns:
            ShippingSnapshot: The saved shipping snapshot.
        """
        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)
        return snapshot

    async def delete(self, snapshot_id):
        """
        Delete a shipping snapshot by ID.
        Args:
            snapshot_id (int): The ID of the shipping snapshot to delete.
        Returns:
            bool: True if deleted, False otherwise.
        """
        snapshot = await self.get_by_id(snapshot_id)
        if snapshot:
            await self.db.delete(snapshot)
            await self.db.commit()
            return True
        return False
