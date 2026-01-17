
# ------------------------------------------------------------------------------
# employee_payment_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing EmployeePayment records from the database.
# Provides methods for retrieving employee payments by ID.
# ------------------------------------------------------------------------------

from backend.persistance.employee_payment import EmployeePayment
from backend.infrastructure.db_types import DBSession
from sqlalchemy import select

class EmployeePaymentRepository:
    """
    Repository for EmployeePayment model.
    Provides methods to retrieve employee payments by ID.
    """
    def __init__(self, db: DBSession):
        """Initialize repository with DB session."""
        self.db = db

    def get_by_id(self, payment_id):
        """Retrieve an employee payment by its ID."""
        result = self.db.execute(
            select(EmployeePayment).filter(EmployeePayment.payment_id == payment_id)
        )
        return result.scalars().first()
