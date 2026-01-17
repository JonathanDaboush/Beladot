

# ------------------------------------------------------------------------------
# paystub_snapshot_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing PaystubSnapshot records from the database.
# Provides async CRUD methods for paystub snapshots.
# ------------------------------------------------------------------------------

from backend.persistance.paystub_snapshot import PaystubSnapshot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class PaystubSnapshotRepository:
    """
    Repository for PaystubSnapshot model.
    Provides async CRUD operations for paystub snapshots.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_by_employee_name(self, employee_name):
        """Retrieve a paystub snapshot by employee name."""
        result = await self.db.execute(
            select(PaystubSnapshot).filter(PaystubSnapshot.employee_name == employee_name)
        )
        return result.scalars().first()

    async def save(self, snapshot):
        """Save a new paystub snapshot to the database."""
        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)
        return snapshot

    async def delete(self, employee_name):
        """Delete a paystub snapshot by employee name."""
        snapshot = await self.get_by_employee_name(employee_name)
        if snapshot:
            await self.db.delete(snapshot)
            await self.db.commit()
            return True
        return False
