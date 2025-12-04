from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    VOIDED = "voided"
    DISPUTED = "disputed"


class PaymentMethod(str, enum.Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"


class Payment(Base):
    """
    SQLAlchemy ORM model for payments table.
    
    Records payment transactions for orders with gateway integration, status tracking,
    and raw response storage for debugging. Supports multiple payment methods and
    refund workflows.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Key: order_id -> orders.id (CASCADE)
        - Indexes: id (primary), order_id, status, transaction_id, created_at
        
    Data Integrity:
        - Amount must be positive
        - Timestamps: updated_at >= created_at
        - Cascading delete when order deleted
        
    Relationships:
        - One-to-one with Order (each order has one payment)
        
    Payment Status Lifecycle:
        1. PENDING: Payment initiated, awaiting processing
        2. AUTHORIZED: Funds reserved (credit card hold)
        3. COMPLETED: Payment captured successfully
        4. FAILED: Payment declined/failed
        5. REFUNDED: Full refund processed
        6. VOIDED: Authorization cancelled before capture
        7. DISPUTED: Chargeback/dispute filed
        
    Payment Methods:
        - CREDIT_CARD: Visa, Mastercard, Amex, etc.
        - DEBIT_CARD: Debit card transactions
        - PAYPAL: PayPal integration
        - STRIPE: Stripe payment gateway
        - BANK_TRANSFER: ACH/wire transfers
        - CASH_ON_DELIVERY: Pay on delivery
        
    Gateway Integration:
        - transaction_id: Payment provider's unique ID (Stripe charge ID, PayPal transaction ID)
        - raw_response: Full JSON response from gateway API (for debugging/reconciliation)
        - Enables idempotent operations via transaction_id lookup
        
    Design Notes:
        - amount_cents: Stored in smallest currency unit (e.g., cents for USD)
        - raw_response: Preserves complete gateway response for auditing
        - Immutable after COMPLETED (updates only for status changes)
        - One payment per order (no split payments)
        
    Financial Reconciliation:
        - Match transaction_id with gateway reports
        - Verify amount_cents matches gateway amount
        - Track failed payments for retry/analysis
        
    Failure Handling:
        - FAILED status: Customer can retry with different method
        - raw_response: Contains gateway error codes/messages
        - Support team uses transaction_id for gateway support tickets
        
    Refund Support:
        - Payment must be COMPLETED to refund
        - Refund records link to this payment via foreign key
        - Status changes to REFUNDED after full refund
        - Partial refunds keep COMPLETED status (tracked via Refund table)
    """
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_cents = Column(Integer, nullable=False)
    method = Column(String(50), nullable=True)  # Payment method as string
    status = Column(SQLEnum(PaymentStatus, values_callable=lambda x: [e.value for e in x]), default=PaymentStatus.PENDING, nullable=False, index=True)
    transaction_id = Column(String(255), nullable=True, index=True)
    raw_response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    order = relationship("Order", back_populates="payment")
    
    __table_args__ = (
        CheckConstraint("amount_cents > 0", name='check_amount_positive'),
        CheckConstraint("updated_at >= created_at", name='check_updated_after_created'),
    )
    
    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, status={self.status}, amount_cents={self.amount_cents})>"
