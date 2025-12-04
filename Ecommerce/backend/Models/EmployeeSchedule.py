"""
Employee Schedule Model

Represents scheduled shifts for employees with coverage tracking.
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, Time, Boolean, ForeignKey, Enum as SQLEnum, Numeric
from sqlalchemy.orm import relationship
from database import Base
import enum


class ShiftType(enum.Enum):
    """Types of shifts."""
    OPENING = "opening"
    CLOSING = "closing"
    MID = "mid"
    FULL_DAY = "full_day"
    SPLIT = "split"
    ON_CALL = "on_call"


class ScheduleStatus(enum.Enum):
    """Schedule entry status."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    COMPLETED = "completed"


class EmployeeSchedule(Base):
    """Employee schedule/shift calendar."""
    
    __tablename__ = "employee_schedules"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("employees.id"), nullable=True)  # Manager who created schedule
    
    # Schedule details
    shift_date = Column(Date, nullable=False)
    shift_start = Column(Time, nullable=False)
    shift_end = Column(Time, nullable=False)
    shift_type = Column(SQLEnum(ShiftType, values_callable=lambda x: [e.value for e in x]), nullable=False, default=ShiftType.FULL_DAY)
    
    # Location/department
    location = Column(String(100), nullable=True)  # Store location, warehouse, etc.
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)  # Position for this shift
    
    # Status
    status = Column(SQLEnum(ScheduleStatus, values_callable=lambda x: [e.value for e in x]), nullable=False, default=ScheduleStatus.SCHEDULED)
    is_confirmed = Column(Boolean, default=False)  # Employee confirmed availability
    confirmed_at = Column(DateTime, nullable=True)
    
    # Coverage
    is_coverage_needed = Column(Boolean, default=False)  # If employee called out
    covered_by = Column(Integer, ForeignKey("employees.id"), nullable=True)  # Who covered the shift
    coverage_notes = Column(String(500), nullable=True)
    
    # Break time
    unpaid_break_minutes = Column(Integer, default=30)  # Lunch break
    paid_break_minutes = Column(Integer, default=15)    # Paid breaks
    
    # Notes
    shift_notes = Column(String(500), nullable=True)
    manager_notes = Column(String(500), nullable=True)
    
    # Audit
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    creator = relationship("Employee", foreign_keys=[created_by])
    cover_employee = relationship("Employee", foreign_keys=[covered_by])
