"""
Shift Swap Model

Allows employees to trade shifts with approval workflow.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


class SwapStatus(enum.Enum):
    """Shift swap request status."""
    PENDING = "pending"
    ACCEPTED_BY_EMPLOYEE = "accepted_by_employee"  # Other employee accepted
    APPROVED = "approved"  # Manager approved
    DENIED = "denied"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ShiftSwap(Base):
    """Shift swap/trade requests between employees."""
    
    __tablename__ = "shift_swaps"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    requesting_employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    target_employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    requesting_shift_id = Column(Integer, ForeignKey("employee_schedules.id"), nullable=False)
    target_shift_id = Column(Integer, ForeignKey("employee_schedules.id"), nullable=True)  # Optional if just giving away
    
    # Approval workflow
    status = Column(SQLEnum(SwapStatus), nullable=False, default=SwapStatus.PENDING)
    accepted_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)  # Manager
    approved_at = Column(DateTime, nullable=True)
    denial_reason = Column(String(500), nullable=True)
    
    # Notes
    request_reason = Column(String(500), nullable=True)
    manager_notes = Column(String(500), nullable=True)
    
    # Audit
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # Relationships
    requesting_employee = relationship("Employee", foreign_keys=[requesting_employee_id])
    target_employee = relationship("Employee", foreign_keys=[target_employee_id])
    requesting_shift = relationship("EmployeeSchedule", foreign_keys=[requesting_shift_id])
    target_shift = relationship("EmployeeSchedule", foreign_keys=[target_shift_id])
    approver = relationship("Employee", foreign_keys=[approved_by])
