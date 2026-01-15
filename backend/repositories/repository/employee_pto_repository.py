
# ------------------------------------------------------------------------------
# employee_pto_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing EmployeePTO records from the database.
# Provides methods for retrieving employee PTO by ID.
# ------------------------------------------------------------------------------

from backend.model.employee_pto import EmployeePTO

class EmployeePTORepository:
    """
    Repository for EmployeePTO model.
    Provides methods to retrieve employee PTO by ID.
    """
    def __init__(self, db):
        """Initialize repository with DB session."""
        self.db = db

    def get_by_id(self, pto_id):
        """Retrieve an employee PTO record by its ID."""
        return self.db.query(EmployeePTO).filter(EmployeePTO.pto_id == pto_id).first()
