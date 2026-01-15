
# ------------------------------------------------------------------------------
# employee_sickday_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing EmployeeSickDay records from the database.
# Provides methods for retrieving employee sick days by ID.
# ------------------------------------------------------------------------------

from backend.model.employee_sickday import EmployeeSickDay

class EmployeeSickDayRepository:
    """
    Repository for EmployeeSickDay model.
    Provides methods to retrieve employee sick days by ID.
    """
    def __init__(self, db):
        """Initialize repository with DB session."""
        self.db = db

    def get_by_id(self, sickday_id):
        """Retrieve an employee sick day record by its ID."""
        return self.db.query(EmployeeSickDay).filter(EmployeeSickDay.sickday_id == sickday_id).first()
