from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime, Date, String, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class SickLeaveStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"


class SickLeaveType(enum.Enum):
    ILLNESS = "illness"
    INJURY = "injury"
    MEDICAL_APPOINTMENT = "medical_appointment"
    FAMILY_CARE = "family_care"
    QUARANTINE = "quarantine"
    OTHER = "other"


class PaidSick(Base):
    """
    Paid Sick Leave accruals and usage.
    
    Separate from PTO for policy clarity and compliance tracking.
    Records sick time accrual, usage, and medical documentation requirements.
    """
    __tablename__ = "paid_sick"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    
    # Sick Leave Request Details
    sick_type = Column(Enum(SickLeaveType), nullable=False, default=SickLeaveType.ILLNESS)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    hours_requested = Column(Numeric(5, 2), nullable=False)
    
    # Status
    status = Column(Enum(SickLeaveStatus), nullable=False, default=SickLeaveStatus.PENDING)
    
    # Medical Documentation
    requires_doctors_note = Column(Boolean, default=False)  # For absences > 3 days
    doctors_note_provided = Column(Boolean, default=False)
    doctors_note_url = Column(String(500), nullable=True)  # Link to stored document
    
    # Approval Workflow
    reported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_by = Column(Integer, nullable=True)  # Manager/HR employee_id
    reviewed_at = Column(DateTime, nullable=True)
    denial_reason = Column(String(500), nullable=True)
    
    # Notes
    reason_notes = Column(String(1000))  # Employee's description
    admin_notes = Column(String(1000))   # Manager/HR notes
    
    # Accrual Impact
    balance_before = Column(Numeric(7, 2), nullable=True)
    balance_after = Column(Numeric(7, 2), nullable=True)
    
    # Intermittent Leave Tracking (FMLA, etc.)
    is_intermittent = Column(Boolean, default=False)
    intermittent_leave_case_id = Column(Integer, nullable=True)
    
    # Payroll Integration
    is_processed = Column(Boolean, default=False, nullable=False)
    payroll_batch_id = Column(Integer, nullable=True)
    
    # Compliance
    is_reportable = Column(Boolean, default=False)  # For workers' comp, disability claims
    workers_comp_claim_number = Column(String(100), nullable=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="paid_sick")
    
    def __repr__(self):
        return f"<PaidSick employee_id={self.employee_id} {self.start_date} to {self.end_date} ({self.hours_requested}h)>"
