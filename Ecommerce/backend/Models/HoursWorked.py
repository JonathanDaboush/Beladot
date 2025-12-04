from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime, Date, String, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
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
    
    # Break Time
    unpaid_break_minutes = Column(Integer, default=0, nullable=False)  # Unpaid break time in minutes
    
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
    
    def __init__(self, **kwargs):
        # Handle 'hours_worked' parameter as shortcut for total hours
        if 'hours_worked' in kwargs:
            hours_value = kwargs.pop('hours_worked')
            # Validate non-negative hours
            if hours_value is not None and hours_value < 0:
                raise ValueError("Hours worked cannot be negative")
            if 'total_hours' not in kwargs:
                kwargs['total_hours'] = hours_value
            # If overtime_hours provided, calculate regular hours
            if 'overtime_hours' in kwargs and 'regular_hours' not in kwargs:
                ot_hours = kwargs['overtime_hours']
                if ot_hours is not None and ot_hours > 0:
                    kwargs['regular_hours'] = hours_value - ot_hours
                else:
                    kwargs['regular_hours'] = hours_value
            elif 'regular_hours' not in kwargs:
                kwargs['regular_hours'] = hours_value
        
        # Validate regular hours is not negative
        if 'regular_hours' in kwargs and kwargs['regular_hours'] is not None:
            if kwargs['regular_hours'] < 0:
                raise ValueError("Regular hours cannot be negative")
        
        # Validate total hours is not negative
        if 'total_hours' in kwargs and kwargs['total_hours'] is not None:
            if kwargs['total_hours'] < 0:
                raise ValueError("Total hours cannot be negative")
        
        # Handle 'status' parameter (map to is_approved)
        if 'status' in kwargs:
            status = kwargs.pop('status')
            if 'is_approved' not in kwargs:
                kwargs['is_approved'] = status == 'approved'
        
        # Handle 'break_time_minutes' parameter (ignore, will be handled separately)
        if 'break_time_minutes' in kwargs:
            kwargs.pop('break_time_minutes')
        
        super().__init__(**kwargs)
    
    @property
    def status(self):
        """Return approval status as string for test compatibility."""
        if self.is_approved:
            return "approved"
        elif self.approved_by and not self.is_approved:
            return "rejected"
        else:
            return "pending"
    
    @property
    def rejected_by(self):
        """Return who rejected this if it was rejected."""
        if not self.is_approved and self.approved_by:
            return self.approved_by
        return None
    
    @property
    def rejection_reason(self):
        """Extract rejection reason from notes."""
        if self.notes and "REJECTED:" in self.notes:
            # Extract the rejection reason
            parts = self.notes.split("REJECTED: ", 1)
            if len(parts) > 1:
                reason_part = parts[1].split(" | Previous notes:", 1)[0]
                return reason_part
        return None
    
    @property
    def break_time_minutes(self):
        """Return stored break time in minutes."""
        # Return the stored unpaid break minutes
        return self.unpaid_break_minutes or 0
    
    def __repr__(self):
        return f"<HoursWorked employee_id={self.employee_id} date={self.work_date} hours={self.total_hours}>"
