
# ------------------------------------------------------------------------------
# department_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing Department records from the database.
# Provides methods for retrieving departments by ID.
# ------------------------------------------------------------------------------

from backend.model.department import Department

class DepartmentRepository:
    """
    Repository for Department model.
    Provides methods to retrieve departments by ID.
    """
    def __init__(self, db):
        """Initialize repository with DB session."""
        self.db = db

    def get_by_id(self, department_id):
        """Retrieve a department by its ID."""
        return self.db.query(Department).filter(Department.department_id == department_id).first()
