
# ------------------------------------------------------------------------------
# manager.py
# ------------------------------------------------------------------------------
# SQLAlchemy ORM model for the manager table.
# This module defines the Manager class, which represents a manager in the
# organization. Each manager is associated with a user and a department, and
# tracks activity status and timestamps.
# ------------------------------------------------------------------------------

from sqlalchemy import Column, BigInteger, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Manager(Base):
    """
    ORM model for the 'manager' table.
    Represents a manager in the organization.

    Attributes:
        manager_id (BigInteger): Primary key for the manager.
        user_id (BigInteger): Foreign key referencing the user.
        department_id (BigInteger): Foreign key referencing the department.
        is_active (Boolean): Whether the manager is currently active.
        created_at (DateTime): Timestamp when the manager record was created.
        last_active_at (DateTime): Timestamp when the manager was last active.
        # Relationships to department, PTO, sick days, shifts, and shift requests are defined elsewhere.
    """
    __tablename__ = 'manager'
    manager_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    department_id = Column(BigInteger, ForeignKey('department.department_id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    last_active_at = Column(DateTime)
    # Relationships (to be completed in department.py, employee_pto.py, employee_sickday.py, shift.py, shift_request.py)
