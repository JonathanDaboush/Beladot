"""
Time Off Request Model

Unified model for all time off requests (PTO, sick, unpaid, etc.)
Links to PaidTimeOff and PaidSick for approved paid leave.
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey, Enum as SQLEnum, Numeric
from sqlalchemy.orm import relationship
from database import Base
import enum


class TimeOffType(enum.Enum):
    """Types of time off."""
    PAID_VACATION = "paid_vacation"
    PAID_SICK = "paid_sick"
    UNPAID = "unpaid"
    BEREAVEMENT = "bereavement"
    JURY_DUTY = "jury_duty"
    MILITARY = "military"
    PARENTAL = "parental"
    FMLA = "fmla"
    WORKERS_COMP = "workers_comp"


class TimeOffStatus(enum.Enum):
    """Time off request status."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"


class TimeOffRequest(Base):
    """Unified time off request with calendar integration."""
    
    __tablename__ = "time_off_requests"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    reviewed_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    paid_time_off_id = Column(Integer, ForeignKey("paid_time_off.id"), nullable=True)  # If paid PTO
    paid_sick_id = Column(Integer, ForeignKey("paid_sick.id"), nullable=True)  # If paid sick
    
    # Request details
    time_off_type = Column(SQLEnum(TimeOffType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Numeric(5, 2), nullable=False)
    is_partial_day = Column(Boolean, default=False)
    partial_hours = Column(Numeric(5, 2), nullable=True)
    
    # Status
    status = Column(SQLEnum(TimeOffStatus), nullable=False, default=TimeOffStatus.PENDING)
    reviewed_at = Column(DateTime, nullable=True)
    denial_reason = Column(String(500), nullable=True)
    
    # Documentation
    reason = Column(String(1000), nullable=True)
    supporting_document_url = Column(String(500), nullable=True)  # Doctor's note, etc.
    
    # Impact
    affects_schedule = Column(Boolean, default=True)  # Automatically cancels scheduled shifts
    affected_shifts_count = Column(Integer, default=0)
    
    # Audit
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="time_off_requests")
    reviewer = relationship("Employee", foreign_keys=[reviewed_by])
    paid_pto = relationship("PaidTimeOff", foreign_keys=[paid_time_off_id])
    paid_sick = relationship("PaidSick", foreign_keys=[paid_sick_id])
