"""
shift.py

Model for shift entity.
Represents a work shift, including assignment, timing, and status.
"""

class Shift:
    def __init__(self, shift_id, department_id, assigned_emp_id, start_time, end_time, created_by_manager_id, status):
        """
        Initialize Shift.
        Args:
            shift_id (int): Unique identifier for the shift.
            department_id (int): Associated department ID.
            assigned_emp_id (int): Employee ID assigned to the shift.
            start_time (datetime): Shift start time.
            end_time (datetime): Shift end time.
            created_by_manager_id (int): Manager ID who created the shift.
            status (str): Status of the shift.
        """
        self.shift_id = shift_id
        self.department_id = department_id
        self.assigned_emp_id = assigned_emp_id
        self.start_time = start_time
        self.end_time = end_time
        self.created_by_manager_id = created_by_manager_id
        self.status = status
