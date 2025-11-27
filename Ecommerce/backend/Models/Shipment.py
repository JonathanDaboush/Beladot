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
    SQLAlchemy ORM model for shipments table.
    
    Manages order fulfillment through carrier integrations, shipping label generation,
    and package tracking. Supports partial shipments, multi-package orders, and
    real-time tracking updates.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Keys: order_id -> orders.id (CASCADE), label_blob_id -> blobs.id (SET NULL)
        - Indexes: id (primary), order_id, tracking_number, status, idempotency_key (unique)
        
    Data Integrity:
        - Cascading delete when order deleted
        - Label blob set to NULL if deleted (preserves shipment record)
        - Idempotency key unique (prevents duplicate label generation)
        - Timestamp ordering for workflow progression
        
    Relationships:
        - Many-to-one with Order (order can have multiple shipments for partial fulfillment)
        - Many-to-one with Blob (shipping label PDF storage)
        - One-to-many with ShipmentItem (links to specific order items and quantities)
        
    Shipment Status Lifecycle:
        1. PENDING: Shipment record created, awaiting label generation
        2. PICKED: Warehouse picked items from inventory
        3. PACKED: Items packed into box, ready for label
        4. SHIPPED: Label generated, package handed to carrier
        5. IN_TRANSIT: Package scanned by carrier, in motion
        6. OUT_FOR_DELIVERY: Package on delivery vehicle
        7. DELIVERED: Package delivered to customer
        8. FAILED: Delivery failed (return to sender, lost, etc.)
        
    Carrier Integration:
        - carrier: FedEx, UPS, USPS, DHL, or Other
        - tracking_number: Carrier-provided tracking ID
        - Carrier APIs: Generate labels, track packages, calculate rates
        - Webhooks: Receive tracking updates from carriers
        
    Label Generation:
        1. Admin creates shipment (order_id, items, quantities)
        2. Validate: ShipmentItem quantities don't exceed OrderItem quantities
        3. Call carrier API with shipping address, package dimensions, weight
        4. Receive label (PDF) and tracking_number
        5. Upload label to Blob storage
        6. Update shipment: status=SHIPPED, tracking_number, label_blob_id
        
    Idempotency:
        - idempotency_key: Prevents duplicate API calls
        - Format: "shipment_{order_id}_{timestamp}_{hash}"
        - If API call fails: Retry with same key (carrier deduplicates)
        - Protects: Network retries, UI double-clicks, concurrent requests
        
    Partial Shipments:
        - Order has 3 items (A: qty 5, B: qty 3, C: qty 2)
        - Shipment 1: A (3), B (3) - Items A and B partially shipped
        - Shipment 2: A (2), C (2) - Remaining A and all C shipped
        - Tracked via ShipmentItem relationship
        - Invariant: Total shipped per OrderItem <= OrderItem.quantity
        
    Shipping Cost:
        - cost_cents: Actual carrier charge (for financial reconciliation)
        - May differ from estimated shipping at checkout
        - Used for: Profit margin analysis, carrier rate comparison
        
    Tracking Updates:
        - Webhooks from carriers update status and timestamps
        - shipped_at: Package handed to carrier
        - estimated_delivery: Carrier's delivery estimate (dynamic)
        - delivered_at: Actual delivery timestamp
        - Customer notifications: Email/SMS on status changes
        
    Failure Handling:
        - status=FAILED: Delivery issue (bad address, customer unavailable, lost)
        - failure_reason: Human-readable explanation for customer support
        - Examples: "Address not found", "Customer refused delivery", "Package lost"
        - Admin actions: Reship, refund, contact customer
        
    Notes Field:
        - Special instructions: "Leave at back door", "Call on arrival"
        - Internal notes: "Fragile - handle with care", "Oversized package"
        - Gift message: "Happy Birthday!"
        
    Design Patterns:
        - Aggregate root: Shipment contains ShipmentItems (composition)
        - Idempotent operations: Safe to retry label generation
        - Event sourcing: Audit log tracks status changes
        - Webhook handling: Update status from carrier notifications
        
    Query Patterns:
        - Order shipments: SELECT * WHERE order_id = X
        - In-transit packages: SELECT * WHERE status IN ('SHIPPED', 'IN_TRANSIT')
        - Overdue deliveries: SELECT * WHERE estimated_delivery < NOW() AND status != 'DELIVERED'
        - Cost analysis: SUM(cost_cents) GROUP BY carrier
        
    Analytics:
        - Delivery time: AVG(delivered_at - shipped_at) GROUP BY carrier
        - Failure rate: COUNT(status='FAILED') / COUNT(*)
        - Carrier performance: Avg delivery time, failure rate per carrier
        
    Customer Experience:
        - Tracking page: Show status, estimated delivery, tracking number
        - Proactive notifications: Email on each status change
        - Map visualization: Show package location (from carrier API)
        - Delivery photo: Some carriers provide proof of delivery
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
