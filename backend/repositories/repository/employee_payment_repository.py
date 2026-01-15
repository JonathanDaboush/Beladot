
# ------------------------------------------------------------------------------
# employee_payment_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing EmployeePayment records from the database.
# Provides methods for retrieving employee payments by ID.
# ------------------------------------------------------------------------------

from backend.model.employee_payment import EmployeePayment

class EmployeePaymentRepository:
    """
    Repository for EmployeePayment model.
    Provides methods to retrieve employee payments by ID.
    """
    def __init__(self, db):
        """Initialize repository with DB session."""
        self.db = db

    def get_by_id(self, payment_id):
        """Retrieve an employee payment by its ID."""
        return self.db.query(EmployeePayment).filter(EmployeePayment.payment_id == payment_id).first()
