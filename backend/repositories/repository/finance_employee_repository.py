
# ------------------------------------------------------------------------------
# finance_employee_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing FinanceEmployee records from the database.
# Provides methods for retrieving finance employees by ID.
# ------------------------------------------------------------------------------

from backend.model.finance_employee import FinanceEmployee

class FinanceEmployeeRepository:
    """
    Repository for FinanceEmployee model.
    Provides methods to retrieve finance employees by ID.
    """
    def __init__(self, db):
        """Initialize repository with DB session."""
        self.db = db

    def get_by_id(self, finance_emp_id):
        """Retrieve a finance employee by their ID."""
        return self.db.query(FinanceEmployee).filter(FinanceEmployee.finance_emp_id == finance_emp_id).first()
