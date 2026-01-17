
# ------------------------------------------------------------------------------
# employee_snapshot_repository.py
# ------------------------------------------------------------------------------
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

# Repository for accessing EmployeeSnapshot records from the database.
# Provides methods for retrieving employee snapshots by full name.
# ------------------------------------------------------------------------------

from backend.persistance.employee_snapshot import EmployeeSnapshot
from sqlalchemy import select

class EmployeeSnapshotRepository:
    """
    Repository for EmployeeSnapshot model.
    Provides methods to retrieve employee snapshots by full name.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with DB session."""
        self.db = db

    async def get_by_id(self, full_name: str) -> Optional[EmployeeSnapshot]:
        """Retrieve an employee snapshot by full name."""
        result = await self.db.execute(
            select(EmployeeSnapshot).filter(EmployeeSnapshot.full_name == full_name)
        )
        return result.scalars().first()
