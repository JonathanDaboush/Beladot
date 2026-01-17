




"""
sickday_snapshot_repository.py

Repository class for managing SickDaySnapshot entities in the database.
Provides async CRUD operations for sick day snapshots by employee name.
"""

from backend.persistance.sickday_snapshot import SickDaySnapshot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class SickDaySnapshotRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_employee_name(self, employee_name):
        """
        Retrieve a SickDaySnapshot by employee name.
        Args:
            employee_name (str): The employee's name.
        Returns:
            SickDaySnapshot or None
        """
        result = await self.db.execute(
            select(SickDaySnapshot).filter(SickDaySnapshot.employee_name == employee_name)
        )
        return result.scalars().first()

    async def save(self, snapshot):
        """
        Save a new sick day snapshot to the database.
        Args:
            snapshot (SickDaySnapshot): The sick day snapshot to save.
        Returns:
            SickDaySnapshot: The saved sick day snapshot.
        """
        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)
        return snapshot

    async def delete(self, employee_name):
        """
        Delete a sick day snapshot by employee name.
        Args:
            employee_name (str): The employee's name.
        Returns:
            bool: True if deleted, False otherwise.
        """
        snapshot = await self.get_by_employee_name(employee_name)
        if snapshot:
            await self.db.delete(snapshot)
            await self.db.commit()
            return True
        return False
