
# ------------------------------------------------------------------------------
# employee_payment_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing EmployeePayment records from the database.
# Provides methods for retrieving employee payments by ID.
# ------------------------------------------------------------------------------

from backend.persistance.employee_payment import EmployeePayment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class EmployeePaymentRepository:
    """
    Repository for EmployeePayment model.
    Provides methods to retrieve employee payments by ID.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_by_id(self, payment_id):
        """Retrieve an employee payment by its ID."""
        result = await self.db.execute(
            select(EmployeePayment).filter(EmployeePayment.payment_id == payment_id)
        )
        return result.scalars().first()
