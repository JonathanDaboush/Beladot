from uuid import UUID
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from Ecommerce.backend.database import Base
import enum

class DeliveryType(enum.Enum):
    outbound = "outbound"
    return_ = "return"

class DeliveryStatus(enum.Enum):
    created = "created"
    shipped = "shipped"
    in_transit = "in_transit"
    delivered = "delivered"
    failed = "failed"
    returned = "returned"
    cancelled = "cancelled"

class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(String, primary_key=True, default=lambda: str(UUID()))
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    shipment_id = Column(String, ForeignKey("shipments.id"), nullable=True)
    return_id = Column(String, ForeignKey("returns.id"), nullable=True)
    delivery_type = Column(Enum(DeliveryType), nullable=False)
    carrier = Column(String, nullable=True)
    tracking_number = Column(String, nullable=True)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.created)
    estimated_delivery = Column(DateTime, nullable=True)
    actual_delivery = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status_history = relationship("DeliveryStatusHistory", back_populates="delivery")

class DeliveryStatusHistory(Base):
    __tablename__ = "delivery_status_history"
    id = Column(String, primary_key=True, default=lambda: str(UUID()))
    delivery_id = Column(String, ForeignKey("deliveries.id"), nullable=False)
    status = Column(Enum(DeliveryStatus), nullable=False)
    location = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)
    delivery = relationship("Delivery", back_populates="status_history")
