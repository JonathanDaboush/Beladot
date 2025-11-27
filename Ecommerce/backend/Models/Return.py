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
    """
    SQLAlchemy ORM model for returns table.
    
    Manages customer return requests with approval workflow, shipment tracking,
    inspection process, and refund integration. Supports partial returns with
    item-level tracking and photo evidence.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Key: order_id -> orders.id (CASCADE)
        - Indexes: id (primary), order_id, status, requested_at
        
    Data Integrity:
        - Reason cannot be empty
        - Cascading delete when order deleted
        - Timestamps track workflow progression
        
    Relationships:
        - Many-to-one with Order (order can have multiple return requests)
        - One-to-one with Refund (return may trigger refund)
        
    Return Status Lifecycle:
        1. REQUESTED: Customer initiates return
        2. APPROVED: Admin approves, provides return label
        3. REJECTED: Return denied (outside window, damaged, etc.)
        4. SHIPPED_BACK: Customer ships items back
        5. RECEIVED: Warehouse receives package
        6. INSPECTED: Items inspected for condition
        7. COMPLETED: Return processed, refund initiated
        
    Item Conditions:
        - NEW: Unopened, original packaging
        - LIKE_NEW: Opened but unused, pristine condition
        - GOOD: Used but functional, minor wear
        - DAMAGED: Broken/defective (customer damaged)
        - DEFECTIVE: Manufacturing defect
        
    Return Items:
        - return_items: JSON array of {order_item_id, quantity, reason}
        - Supports partial returns (not all items)
        - Example: [{"order_item_id": 123, "quantity": 2, "reason": "Wrong size"}]
        
    Photo Evidence:
        - photos: JSON array of blob_ids or URLs
        - Required for damage/defect claims
        - Attached during return request or inspection
        
    Design Notes:
        - reason: Customer explanation (size, quality, damaged, etc.)
        - item_condition: Assessed during inspection phase
        - inspection_notes: Warehouse notes on item condition
        - admin_notes: Internal notes for customer service
        - tracking_number: Return shipment tracking
        
    Inspection Process:
        1. RECEIVED: Package arrives at warehouse
        2. INSPECTED: QA checks item condition
        3. item_condition set (NEW, DAMAGED, etc.)
        4. inspection_notes recorded
        5. COMPLETED: Trigger refund or deny
        
    Refund Integration:
        - One-to-one relationship with Refund
        - Approved returns trigger refund creation
        - Restocking fees applied based on item_condition
        - Refund amount = order amount - restocking fee - original shipping
        
    Workflow Timestamps:
        - requested_at: Customer submits return
        - approved_at: Admin approves return
        - rejected_at: Admin denies return
        - shipped_back_at: Customer ships package
        - received_at: Warehouse receives package
        - inspected_at: Inspection completed
        - completed_at: Refund processed
        
    Business Rules:
        - Return window: 30 days from delivery
        - Free return shipping for defects
        - Restocking fee for buyer's remorse
        - Photos required for damage claims
    """
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
