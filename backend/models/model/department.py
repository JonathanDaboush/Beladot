"""
department.py

SQLAlchemy model for Department entity.
Represents a business department and its relationships to employee components.
"""

from sqlalchemy.orm import relationship

class Department:
    """
    Department model representing a business department.
    Attributes:
        department_id (int): Unique identifier for the department.
        name (str): Name of the department.
        employee_components (list): Related employee components.
    """
    def __init__(self, department_id, name):
        """
        Initialize Department with ID and name.
        Args:
            department_id (int): Unique identifier for the department.
            name (str): Name of the department.
        """
        self.department_id = department_id
        self.name = name
    # SQLAlchemy ORM relationship for employee components
    employee_components = relationship('EmployeeComponent', back_populates='department')
