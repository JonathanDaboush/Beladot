"""
employee_pto.py

Model for Employee Paid Time Off (PTO) requests, including status, approval, and date tracking.
Represents an employee's PTO request for HR and payroll processing.
"""
from backend.model.enums import PTOStatus

class EmployeePTO:
    """
    Represents an employee's PTO request.
    Tracks request status, approval, and relevant dates.
    """
    def __init__(self, pto_id, emp_id, start_date, end_date, status=PTOStatus.REQUESTED, approved_by_manager_id=None, created_at=None, updated_at=None):
        """
        Initialize an EmployeePTO instance.
        Args:
            pto_id: Unique PTO request ID
            emp_id: Employee ID
            start_date: PTO start date
            end_date: PTO end date
            status: PTOStatus enum value
            approved_by_manager_id: Manager ID who approved
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.pto_id = pto_id
        self.emp_id = emp_id
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.approved_by_manager_id = approved_by_manager_id
        self.created_at = created_at
        self.updated_at = updated_at
