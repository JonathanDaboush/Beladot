"""
reimbursement_snapshot.py

Model for reimbursement snapshot entity.
Represents a snapshot of a reimbursement, including employee, amount, and description.
"""

class ReimbursementSnapshot:
    def __init__(self, employee_name, amount, description, created_at):
        """
        Initialize ReimbursementSnapshot.
        Args:
            employee_name (str): Name of the employee.
            amount (float): Reimbursement amount.
            description (str): Description of the reimbursement.
            created_at (datetime): Creation timestamp.
        """
        self.employee_name = employee_name
        self.amount = amount
        self.description = description
        self.created_at = created_at
