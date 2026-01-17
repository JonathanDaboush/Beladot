
# ------------------------------------------------------------------------------
# address_snapshot_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing AddressSnapshot records from the database.
# Provides async methods for retrieving address snapshots by order number.
# ------------------------------------------------------------------------------

from backend.persistance.address_snapshot import AddressSnapshot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class AddressSnapshotRepository:
    """
    Repository for AddressSnapshot model.
    Provides async methods to retrieve address snapshots by order number.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_by_id(self, order_number):
        """Retrieve an AddressSnapshot by order number."""
        result = await self.db.execute(
            select(AddressSnapshot).filter(AddressSnapshot.order_number == order_number)
        )
        return result.scalars().first()
