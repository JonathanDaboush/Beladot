

# ------------------------------------------------------------------------------
# pto_snapshot_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing PTOSnapshot records from the database.
# Provides async CRUD methods for PTO snapshots.
# ------------------------------------------------------------------------------

from backend.model.pto_snapshot import PTOSnapshot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class PTOSnapshotRepository:
    """
    Repository for PTOSnapshot model.
    Provides async CRUD operations for PTO snapshots.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_by_employee_name(self, employee_name):
        """Retrieve a PTO snapshot by employee name."""
        result = await self.db.execute(
            select(PTOSnapshot).filter(PTOSnapshot.employee_name == employee_name)
        )
        return result.scalars().first()

    async def save(self, snapshot):
        """Save a new PTO snapshot to the database."""
        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)
        return snapshot

    async def delete(self, employee_name):
        """Delete a PTO snapshot by employee name."""
        snapshot = await self.get_by_employee_name(employee_name)
        if snapshot:
            await self.db.delete(snapshot)
            await self.db.commit()
            return True
        return False
