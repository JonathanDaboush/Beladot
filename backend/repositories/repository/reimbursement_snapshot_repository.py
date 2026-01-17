




"""
reimbursement_snapshot_repository.py

Repository class for managing ReimbursementSnapshot entities in the database.
Provides async CRUD operations for reimbursement snapshots by employee name.
"""

from backend.persistance.reimbursement_snapshot import ReimbursementSnapshot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class ReimbursementSnapshotRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_employee_name(self, employee_name):
        """
        Retrieve a ReimbursementSnapshot by employee name.
        Args:
            employee_name (str): The employee's name.
        Returns:
            ReimbursementSnapshot or None
        """
        result = await self.db.execute(
            select(ReimbursementSnapshot).filter(ReimbursementSnapshot.employee_name == employee_name)
        )
        return result.scalars().first()

    async def save(self, snapshot):
        """
        Save a new reimbursement snapshot to the database.
        Args:
            snapshot (ReimbursementSnapshot): The snapshot to save.
        Returns:
            ReimbursementSnapshot: The saved snapshot.
        """
        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)
        return snapshot

    async def delete(self, employee_name):
        """
        Delete a reimbursement snapshot by employee name.
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
