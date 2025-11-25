from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class RefundStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class Refund(Base):
    __tablename__ = "refunds"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="RESTRICT"), nullable=False)
    return_id = Column(Integer, ForeignKey("returns.id", ondelete="SET NULL"), nullable=True, index=True)
    amount_cents = Column(Integer, nullable=False)
    restocking_fee_cents = Column(Integer, default=0, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(SQLEnum(RefundStatus), default=RefundStatus.PENDING, nullable=False, index=True)
    gateway_transaction_id = Column(String(255), nullable=True, index=True)
    idempotency_key = Column(String(255), unique=True, nullable=True, index=True)
    admin_notes = Column(Text, nullable=True)
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    order = relationship("Order", back_populates="refunds")
    payment = relationship("Payment")
    return_request = relationship("Return", back_populates="refund")
    
    __table_args__ = (
        CheckConstraint("amount_cents > 0", name='check_amount_positive'),
        CheckConstraint("restocking_fee_cents >= 0", name='check_restocking_fee_non_negative'),
        CheckConstraint("length(trim(reason)) > 0", name='check_reason_present'),
        CheckConstraint("approved_at IS NULL OR approved_at >= requested_at", name='check_approved_after_requested'),
        CheckConstraint("processed_at IS NULL OR (approved_at IS NOT NULL AND processed_at >= approved_at)", name='check_processed_after_approved'),
    )
    
    def __repr__(self):
        return f"<Refund(id={self.id}, order_id={self.order_id}, status={self.status}, amount_cents={self.amount_cents})>"
