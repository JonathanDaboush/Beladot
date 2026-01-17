
# ------------------------------------------------------------------------------
# employee_sickday_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing EmployeeSickDay records from the database.
# Provides methods for retrieving employee sick days by ID.
# ------------------------------------------------------------------------------

from typing import Optional
from backend.persistance.employee_sickday import EmployeeSickDay
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class EmployeeSickDayRepository:
    """
    Repository for EmployeeSickDay model.
    Provides methods to retrieve employee sick days by ID.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with DB session."""
        self.db = db

    async def get_by_id(self, sickday_id: int) -> Optional[EmployeeSickDay]:
        """Retrieve an employee sick day record by its ID."""
        result = await self.db.execute(
            select(EmployeeSickDay).filter(EmployeeSickDay.sickday_id == sickday_id)
        )
        return result.scalars().first()
