from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime, Date, String, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class PTOStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"


class PTOType(enum.Enum):
    VACATION = "vacation"
    PERSONAL = "personal"
    BEREAVEMENT = "bereavement"
    JURY_DUTY = "jury_duty"
    OTHER = "other"


class PaidTimeOff(Base):
    """
    Paid Time Off (PTO) accruals and usage.
    
    Tracks vacation days, personal time, and other paid time off.
    Records accrual rates, balances, and usage history.
    """
    __tablename__ = "paid_time_off"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    
    # PTO Request Details
    pto_type = Column(Enum(PTOType), nullable=False, default=PTOType.VACATION)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    hours_requested = Column(Numeric(5, 2), nullable=False)  # Total hours requested
    
    # Status
    status = Column(Enum(PTOStatus), nullable=False, default=PTOStatus.PENDING)
    
    # Approval Workflow
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_by = Column(Integer, nullable=True)  # Manager employee_id
    reviewed_at = Column(DateTime, nullable=True)
    denial_reason = Column(String(500), nullable=True)
    
    # Notes
    request_notes = Column(String(1000))  # Employee's notes
    admin_notes = Column(String(1000))    # Manager/HR notes
    
    # Accrual Impact
    balance_before = Column(Numeric(7, 2), nullable=True)  # PTO balance before this request
    balance_after = Column(Numeric(7, 2), nullable=True)   # PTO balance after deduction
    
    # Payroll Integration
    is_processed = Column(Boolean, default=False, nullable=False)
    payroll_batch_id = Column(Integer, nullable=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="paid_time_off")
    
    def __repr__(self):
        return f"<PaidTimeOff employee_id={self.employee_id} {self.start_date} to {self.end_date} ({self.hours_requested}h)>"
