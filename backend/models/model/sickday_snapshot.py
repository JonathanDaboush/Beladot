"""
sickday_snapshot.py

Model for sick day snapshot entity.
Represents a snapshot of an employee's sick days for a given period.
"""

class SickDaySnapshot:
    def __init__(self, employee_name, sick_days, created_at):
        """
        Initialize SickDaySnapshot.
        Args:
            employee_name (str): Name of the employee.
            sick_days (int): Number of sick days taken.
            created_at (datetime): Creation timestamp.
        """
        self.employee_name = employee_name
        self.sick_days = sick_days
        self.created_at = created_at
