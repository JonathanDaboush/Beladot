
# ------------------------------------------------------------------------------
# department_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing Department records from the database.
# Provides methods for retrieving departments by ID.
# ------------------------------------------------------------------------------

from typing import Optional
from backend.persistance.department import Department
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class DepartmentRepository:
    """
    Repository for Department model.
    Provides methods to retrieve departments by ID.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with DB session."""
        self.db = db

    async def get_by_id(self, department_id: int) -> Optional[Department]:
        """Retrieve a department by its ID."""
        result = await self.db.execute(
            select(Department).filter(Department.department_id == department_id)
        )
        return result.scalars().first()
