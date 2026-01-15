"""
employee_sickday.py

Model for Employee Sick Day requests, including status, approval, and date tracking.
Represents an employee's sick day request for HR and payroll processing.
"""
from backend.model.enums import PTOStatus

class EmployeeSickDay:
    """
    Represents an employee's sick day request.
    Tracks request status, approval, and relevant dates.
    """
    def __init__(self, sickday_id, emp_id, date, status=PTOStatus.REQUESTED, approved_by_manager_id=None, created_at=None, updated_at=None):
        """
        Initialize an EmployeeSickDay instance.
        Args:
            sickday_id: Unique sick day request ID
            emp_id: Employee ID
            date: Sick day date
            status: PTOStatus enum value
            approved_by_manager_id: Manager ID who approved
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.sickday_id = sickday_id
        self.emp_id = emp_id
        self.date = date
        self.status = status
        self.approved_by_manager_id = approved_by_manager_id
        self.created_at = created_at
        self.updated_at = updated_at
