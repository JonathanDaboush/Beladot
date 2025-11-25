from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)
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
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_number={self.order_number}, status={self.status})>"
