
# ------------------------------------------------------------------------------
# employee_snapshot_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing EmployeeSnapshot records from the database.
# Provides methods for retrieving employee snapshots by full name.
# ------------------------------------------------------------------------------

from backend.model.employee_snapshot import EmployeeSnapshot

class EmployeeSnapshotRepository:
    """
    Repository for EmployeeSnapshot model.
    Provides methods to retrieve employee snapshots by full name.
    """
    def __init__(self, db):
        """Initialize repository with DB session."""
        self.db = db

    def get_by_id(self, full_name):
        """Retrieve an employee snapshot by full name."""
        return self.db.query(EmployeeSnapshot).filter(EmployeeSnapshot.full_name == full_name).first()
