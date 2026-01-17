
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

# ------------------------------------------------------------------------------
# employee_pto_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing EmployeePTO records from the database.
# Provides methods for retrieving employee PTO by ID.
# ------------------------------------------------------------------------------

from backend.persistance.employee_pto import EmployeePTO
from sqlalchemy import select

class EmployeePTORepository:
    """
    Repository for EmployeePTO model.
    Provides methods to retrieve employee PTO by ID.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with DB session."""
        self.db = db

    async def get_by_id(self, pto_id: int) -> Optional[EmployeePTO]:
        """Retrieve an employee PTO record by its ID."""
        result = await self.db.execute(
            select(EmployeePTO).filter(EmployeePTO.pto_id == pto_id)
        )
        return result.scalars().first()
