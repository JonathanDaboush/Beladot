
# ------------------------------------------------------------------------------
# employee.py
# ------------------------------------------------------------------------------
# SQLAlchemy ORM model for the employee table.
# This module defines the Employee class, which represents an employee in the
# organization. Each employee is associated with a user and a department.
# Relationships to PTO, sick days, shifts, and payments are defined elsewhere.
# ------------------------------------------------------------------------------

from sqlalchemy import Column, BigInteger, ForeignKey, String
from sqlalchemy.orm import relationship
from .base import Base

class Employee(Base):
    """
    ORM model for the 'employee' table.
    Represents an employee in the organization.

    Attributes:
        emp_id (BigInteger): Primary key for the employee.
        user_id (BigInteger): Foreign key referencing the user.
        department_id (BigInteger): Foreign key referencing the department.
        # Relationships to PTO, sick days, shifts, and payments are defined elsewhere.
    """
    __tablename__ = 'employee'
    emp_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    department_id = Column(BigInteger, ForeignKey('department.department_id'))
    notes = Column(String(255), nullable=True)  # Temporary field for update testing
    # Relationships (to be completed in employee_pto.py, employee_sickday.py, shift.py, shift_request.py, finance_employee.py, employee_payment.py)
