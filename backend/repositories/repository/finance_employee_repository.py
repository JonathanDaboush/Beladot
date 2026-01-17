
# ------------------------------------------------------------------------------
# finance_employee_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing FinanceEmployee records from the database.
# Provides methods for retrieving finance employees by ID.
# ------------------------------------------------------------------------------

from typing import Optional
from backend.persistance.finance_employee import FinanceEmployee
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class FinanceEmployeeRepository:
    """
    Repository for FinanceEmployee model.
    Provides methods to retrieve finance employees by ID.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with DB session."""
        self.db = db

    async def get_by_id(self, finance_emp_id: int) -> Optional[FinanceEmployee]:
        """Retrieve a finance employee by their ID."""
        result = await self.db.execute(
            select(FinanceEmployee).filter(FinanceEmployee.finance_emp_id == finance_emp_id)
        )
        return result.scalars().first()
