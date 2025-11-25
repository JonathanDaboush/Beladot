from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class ShipmentStatus(str, enum.Enum):
    PENDING = "pending"
    PICKED = "picked"
    PACKED = "packed"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED = "failed"


class ShipmentCarrier(str, enum.Enum):
    """Supported shipping carriers for label generation."""
    FEDEX = "fedex"
    UPS = "ups"
    USPS = "usps"
    DHL = "dhl"
    OTHER = "other"


class Shipment(Base):
    """
    Fulfillment unit connecting an Order to carrier logistics.
    
    Responsibilities:
    - Generate shipping labels via carrier APIs (idempotently using idempotency_key)
    - Store label blobs for download/printing
    - Provide tracking updates to customers
    - Map Order → ShipmentItems with quantity validation
    
    Failure modes:
    - Failed label creation (bad addresses, carrier limits)
    - Surface clear errors in failure_reason for admin retry
    
    Invariant: Sum of shipment_items.quantity per order_item must not exceed order_item.quantity
    (enforced via application-level validation before shipment creation)
    """
    __tablename__ = "shipments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    tracking_number = Column(String(100), nullable=True, index=True)
    carrier = Column(SQLEnum(ShipmentCarrier), nullable=True)
    status = Column(SQLEnum(ShipmentStatus), default=ShipmentStatus.PENDING, nullable=False, index=True)
    
    # Idempotency for carrier API calls (prevent duplicate label generation)
    idempotency_key = Column(String(100), unique=True, nullable=True, index=True)
    
    # Shipping label reference
    label_blob_id = Column(Integer, ForeignKey("blobs.id", ondelete="SET NULL"), nullable=True)
    cost_cents = Column(Integer, nullable=True)
    
    # Failure tracking for admin retry paths
    failure_reason = Column(Text, nullable=True)
    
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    estimated_delivery = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="shipments")
    items = relationship("ShipmentItem", back_populates="shipment", cascade="all, delete-orphan")
    label_blob = relationship("Blob")
    
    # Constraints
    __table_args__ = (
        # Tracking number uniqueness when present (nullable for pending shipments)
        UniqueConstraint("tracking_number", name="uq_shipment_tracking_number", postgresql_where="tracking_number IS NOT NULL"),
        
        # Timing constraints: delivered_at >= shipped_at
        CheckConstraint("delivered_at IS NULL OR shipped_at IS NULL OR delivered_at >= shipped_at", name="ck_shipment_delivery_after_shipping"),
        
        # Timestamps: updated_at >= created_at
        CheckConstraint("updated_at >= created_at", name="ck_shipment_updated_after_created"),
        
        # Cost validation: non-negative when present
        CheckConstraint("cost_cents IS NULL OR cost_cents >= 0", name="ck_shipment_cost_nonnegative"),
        
        # Shipped shipments must have tracking number and carrier
        CheckConstraint(
            "status NOT IN ('shipped', 'in_transit', 'out_for_delivery', 'delivered') OR (tracking_number IS NOT NULL AND carrier IS NOT NULL)",
            name="ck_shipment_shipped_requires_tracking"
        ),
        
        # Delivered shipments must have delivered_at timestamp
        CheckConstraint(
            "status != 'delivered' OR delivered_at IS NOT NULL",
            name="ck_shipment_delivered_requires_timestamp"
        ),
        
        # Failed shipments should have failure_reason
        CheckConstraint(
            "status != 'failed' OR failure_reason IS NOT NULL",
            name="ck_shipment_failed_requires_reason"
        ),
        
        # Shipped shipments must have label blob (for download/printing)
        CheckConstraint(
            "status NOT IN ('shipped', 'in_transit', 'out_for_delivery', 'delivered') OR label_blob_id IS NOT NULL",
            name="ck_shipment_shipped_requires_label"
        ),
        
        # Index for customer status queries
        Index("ix_shipment_order_status", "order_id", "status"),
    )
    
    def __repr__(self):
        return f"<Shipment(id={self.id}, tracking_number={self.tracking_number}, status={self.status})>"
