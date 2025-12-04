from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class OrderStatus(str, enum.Enum):
    """
    Order lifecycle states.
    
    Workflow:
        pending → confirmed → processing → shipped → delivered
        Any state → cancelled or refunded
    """
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Order(Base):
    """
    SQLAlchemy ORM model for orders table.
    
    Complete order record with denormalized shipping address, pricing breakdown,
    and order lifecycle tracking. Central entity for fulfillment operations.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Key: user_id -> users.id (CASCADE delete)
        - Unique Constraint: order_number
        - Indexes: id, user_id, order_number, status, created_at
        
    Data Integrity:
        - Order number non-empty and unique
        - All price components non-negative
        - total_cents = subtotal + tax + shipping - discount (enforced)
        - Shipping address fields required and validated
        - Country exactly 2 characters (ISO-2)
        - updated_at >= created_at
        - Cascading relationships for items, payment, shipments, refunds, returns
        
    Relationships:
        - Many-to-one with User
        - One-to-many with OrderItem (cascade delete)
        - One-to-one with Payment (cascade delete)
        - One-to-many with Shipment (cascade delete)
        - One-to-many with Refund (cascade delete)
        - One-to-many with Return (cascade delete)
        
    Design Notes:
        - Shipping address denormalized (snapshot at order time)
        - Prices in cents (avoids floating-point issues)
        - order_number for human-readable reference
        - customer_notes and admin_notes separated for access control
        - Status enum controls workflow state machine
        - Total calculation enforced at database level
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    idempotency_key = Column(String(255), unique=True, nullable=True, index=True)  # For duplicate prevention
    status = Column(SQLEnum(OrderStatus, values_callable=lambda x: [e.value for e in x]), default=OrderStatus.PENDING, nullable=False, index=True)
    subtotal_cents = Column(Integer, nullable=False)
    tax_cents = Column(Integer, default=0, nullable=False)
    shipping_cost_cents = Column(Integer, default=0, nullable=False)
    discount_cents = Column(Integer, default=0, nullable=False)
    total_cents = Column(Integer, nullable=False)
    shipping_address_line1 = Column(String(255), nullable=False)
    shipping_address_line2 = Column(String(255), nullable=True)
    shipping_city = Column(String(100), nullable=False)
    shipping_state = Column(String(100), nullable=False)
    shipping_country = Column(String(2), nullable=False)
    shipping_postal_code = Column(String(20), nullable=False)
    customer_notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="order", cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="order", cascade="all, delete-orphan")
    returns = relationship("Return", back_populates="order", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("length(trim(order_number)) > 0", name='check_order_number_present'),
        CheckConstraint("subtotal_cents >= 0", name='check_subtotal_non_negative'),
        CheckConstraint("tax_cents >= 0", name='check_tax_non_negative'),
        CheckConstraint("shipping_cost_cents >= 0", name='check_shipping_cost_non_negative'),
        CheckConstraint("discount_cents >= 0", name='check_discount_non_negative'),
        CheckConstraint("total_cents >= 0", name='check_total_non_negative'),
        CheckConstraint("total_cents = subtotal_cents + tax_cents + shipping_cost_cents - discount_cents", name='check_total_equals_sum'),
        CheckConstraint("length(trim(shipping_address_line1)) > 0", name='check_shipping_address_present'),
        CheckConstraint("length(trim(shipping_city)) > 0", name='check_shipping_city_present'),
        CheckConstraint("length(trim(shipping_state)) > 0", name='check_shipping_state_present'),
        CheckConstraint("length(shipping_country) = 2", name='check_shipping_country_iso2'),
        CheckConstraint("length(trim(shipping_postal_code)) > 0", name='check_shipping_postal_code_present'),
        CheckConstraint("updated_at >= created_at", name='check_updated_after_created'),
    )
    
    @property
    def total(self):
        """Convert total_cents to Decimal dollars."""
        from decimal import Decimal
        return Decimal(str(self.total_cents / 100))
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_number={self.order_number}, status={self.status})>"
