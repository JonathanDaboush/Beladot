"""
finance_employee.py

Model for finance employee entity.
Represents a finance employee and their activity status.
"""

class FinanceEmployee:
    def __init__(self, finance_emp_id, emp_id, is_active, created_at, last_active_at):
        """
        Initialize FinanceEmployee.
        Args:
            finance_emp_id (int): Unique identifier for the finance employee.
            emp_id (int): Employee ID.
            is_active (bool): Whether the finance employee is active.
            created_at (datetime): Creation timestamp.
            last_active_at (datetime): Last active timestamp.
        """
        self.finance_emp_id = finance_emp_id
        self.emp_id = emp_id
        self.is_active = is_active
        self.created_at = created_at
        self.last_active_at = last_active_at
