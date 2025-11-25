from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class ReturnStatus(str, enum.Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    SHIPPED_BACK = "shipped_back"
    RECEIVED = "received"
    INSPECTED = "inspected"
    COMPLETED = "completed"


class ItemCondition(str, enum.Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    GOOD = "good"
    DAMAGED = "damaged"
    DEFECTIVE = "defective"


class Return(Base):
    __tablename__ = "returns"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    reason = Column(Text, nullable=False)
    item_condition = Column(SQLEnum(ItemCondition), nullable=True)
    status = Column(SQLEnum(ReturnStatus), default=ReturnStatus.REQUESTED, nullable=False, index=True)
    return_items = Column(JSON, nullable=True)
    photos = Column(JSON, nullable=True)
    tracking_number = Column(String(255), nullable=True)
    inspection_notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    shipped_back_at = Column(DateTime(timezone=True), nullable=True)
    received_at = Column(DateTime(timezone=True), nullable=True)
    inspected_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    order = relationship("Order", back_populates="returns")
    refund = relationship("Refund", back_populates="return_request", uselist=False)
    
    __table_args__ = (
        CheckConstraint("length(trim(reason)) > 0", name='check_reason_present'),
        CheckConstraint("approved_at IS NULL OR approved_at >= requested_at", name='check_approved_after_requested'),
        CheckConstraint("rejected_at IS NULL OR rejected_at >= requested_at", name='check_rejected_after_requested'),
        CheckConstraint("received_at IS NULL OR received_at >= requested_at", name='check_received_after_requested'),
        CheckConstraint("inspected_at IS NULL OR (received_at IS NOT NULL AND inspected_at >= received_at)", name='check_inspected_after_received'),
        CheckConstraint("completed_at IS NULL OR completed_at >= requested_at", name='check_completed_after_requested'),
    )
    
    def __repr__(self):
        return f"<Return(id={self.id}, order_id={self.order_id}, status={self.status})>"
