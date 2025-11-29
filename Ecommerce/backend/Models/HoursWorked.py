from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime, Date, String, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class HoursType(enum.Enum):
    REGULAR = "regular"
    OVERTIME = "overtime"
    DOUBLE_TIME = "double_time"
    HOLIDAY = "holiday"


class HoursWorked(Base):
    """
    Time slices for payroll consumption.
    
    Records regular hours, overtime, and special time entries
    for accurate payroll calculation and time tracking.
    """
    __tablename__ = "hours_worked"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    
    # Time Period
    work_date = Column(Date, nullable=False, index=True)
    clock_in = Column(DateTime, nullable=True)
    clock_out = Column(DateTime, nullable=True)
    
    # Hours Breakdown
    regular_hours = Column(Numeric(5, 2), default=0.00, nullable=False)
    overtime_hours = Column(Numeric(5, 2), default=0.00, nullable=False)
    double_time_hours = Column(Numeric(5, 2), default=0.00, nullable=False)
    holiday_hours = Column(Numeric(5, 2), default=0.00, nullable=False)
    
    # Total
    total_hours = Column(Numeric(5, 2), nullable=False)  # Sum of all hour types
    
    # Additional Context
    hours_type = Column(Enum(HoursType), default=HoursType.REGULAR, nullable=False)
    notes = Column(String(500))  # Reason for overtime, special circumstances
    
    # Approval Workflow
    is_approved = Column(Boolean, default=False, nullable=False)
    approved_by = Column(Integer, nullable=True)  # Manager employee_id
    approved_at = Column(DateTime, nullable=True)
    
    # Payroll Processing
    is_paid = Column(Boolean, default=False, nullable=False)
    payroll_batch_id = Column(Integer, nullable=True)  # Link to payroll run
    paid_at = Column(DateTime, nullable=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="hours_worked")
    
    def __repr__(self):
        return f"<HoursWorked employee_id={self.employee_id} date={self.work_date} hours={self.total_hours}>"
