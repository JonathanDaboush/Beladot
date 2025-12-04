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
    """
    SQLAlchemy ORM model for refunds table.
    
    Manages customer refunds with payment gateway integration, approval workflow,
    and optional restocking fees. Supports both return-based and standalone refunds.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Keys: order_id -> orders.id (CASCADE), payment_id -> payments.id (RESTRICT),
                       return_id -> returns.id (SET NULL)
        - Indexes: id (primary), order_id, return_id, status, gateway_transaction_id,
                   idempotency_key (unique), requested_at
        
    Data Integrity:
        - Amount must be positive
        - Restocking fee must be non-negative
        - Reason cannot be empty
        - Approval timestamp must be after request timestamp
        - Processing timestamp must be after approval timestamp
        - Payment deletion prevented (RESTRICT) to preserve refund history
        
    Relationships:
        - Many-to-one with Order (order can have multiple refunds)
        - Many-to-one with Payment (refund tied to specific payment)
        - One-to-one with Return (optional, refund may not be for return)
        
    Refund Workflow:
        1. PENDING: Customer requests refund
        2. APPROVED: Admin reviews and approves
        3. PROCESSING: Gateway API call initiated
        4. PROCESSED: Funds returned to customer
        5. REJECTED: Admin denies refund
        6. FAILED: Gateway error (retry possible)
        
    Refund Types:
        - Return-based: Linked to Return record (return_id populated)
        - Standalone: Not linked to return (damaged goods, customer service)
        
    Gateway Integration:
        - gateway_transaction_id: Payment provider's refund ID
        - idempotency_key: Prevents duplicate refund requests
        - Status tracking: Maps to provider's refund states
        
    Restocking Fee:
        - restocking_fee_cents: Deducted from refund amount
        - Applied for open-box returns, custom items, etc.
        - Net refund = amount_cents - restocking_fee_cents
        
    Design Notes:
        - idempotency_key: Unique per refund attempt (prevents double refunds)
        - reason: Customer-provided explanation
        - admin_notes: Internal notes for review/processing
        - Timestamps track workflow progression
        - RESTRICT on payment: Cannot delete payment with pending refunds
        
    Financial Reconciliation:
        - Total refunded per order: SUM(amount_cents) WHERE order_id = X
        - Refund rate: COUNT(refunds) / COUNT(orders)
        - Average refund: AVG(amount_cents)
        
    Failure Recovery:
        - FAILED status: Admin can retry processing
        - gateway_transaction_id: Idempotent gateway calls
        - Partial refunds: Multiple refunds per order allowed
    """
    __tablename__ = "refunds"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="RESTRICT"), nullable=False)
    return_id = Column(Integer, ForeignKey("returns.id", ondelete="SET NULL"), nullable=True, index=True)
    amount_cents = Column(Integer, nullable=False)
    restocking_fee_cents = Column(Integer, default=0, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(SQLEnum(RefundStatus, values_callable=lambda x: [e.value for e in x]), default=RefundStatus.PENDING, nullable=False, index=True)
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
