from uuid import UUID
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from Ecommerce.backend.database import Base
import enum

class DeliveryType(enum.Enum):
    outbound = "outbound"
    return_ = "return"

class DeliveryStatus(enum.Enum):
    created = "created"
    label_created = "label_created"
    picked_up = "picked_up"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    delivery_failed = "delivery_failed"
    exception = "exception"
    customs_hold = "customs_hold"
    returned = "returned"
    cancelled = "cancelled"

class Delivery(Base):
    """
    Delivery tracking model for third-party carrier integrations.
    
    Your platform doesn't own logistics - this model stores references to
    carrier shipments (Purolator, FedEx, DHL, UPS, Canada Post) and tracks
    their status via API integrations and webhooks.
    
    Architecture:
        - Carrier agnostic: Supports multiple carriers via adapter pattern
        - Event-driven: Updates via webhooks from carriers
        - Polling fallback: Background job syncs for carriers without webhooks
        - International ready: Customs, duties, multi-currency support
    
    Relationships:
        - order_id: The order being delivered
        - shipment_id: Internal shipment grouping (multi-package orders)
        - return_id: If this is a return shipment
    
    Carrier Integration Flow:
        1. Customer completes checkout → create Delivery record (status=created)
        2. Call carrier API → generate label, get tracking number
        3. Update with tracking_number, label_url (status=label_created)
        4. Carrier picks up → webhook updates status=picked_up
        5. Package scans → tracking_events array grows
        6. Delivered → webhook updates status=delivered, proof stored
    
    Security:
        - API keys stored in config, not in model
        - Webhook signatures verified before processing
        - Tracking URLs are public but don't expose sensitive order data
    """
    __tablename__ = "deliveries"
    
    # Identity
    id = Column(String, primary_key=True, default=lambda: str(UUID()))
    order_id = Column(String, ForeignKey("orders.id"), nullable=False, index=True)
    shipment_id = Column(String, ForeignKey("shipments.id"), nullable=True)
    return_id = Column(String, ForeignKey("returns.id"), nullable=True, index=True)
    delivery_type = Column(Enum(DeliveryType), nullable=False)
    
    # Carrier Information (external service, not owned by you)
    carrier = Column(String, nullable=True, index=True)  # "purolator", "fedex", "dhl", "ups", "canadapost"
    service_level = Column(String, nullable=True)  # "express", "ground", "overnight", "international"
    tracking_number = Column(String, nullable=True, unique=True, index=True)  # Carrier's tracking ID
    tracking_url = Column(String, nullable=True)  # Deep link to carrier's tracking page
    label_url = Column(String, nullable=True)  # PDF shipping label from carrier API
    
    # Status & Timing
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.created, index=True)
    shipped_at = Column(DateTime, nullable=True)  # When carrier picked up
    estimated_delivery = Column(DateTime, nullable=True)  # From carrier's API
    actual_delivery = Column(DateTime, nullable=True)  # Confirmed delivery time
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Tracking Events (synced from carrier API/webhooks)
    tracking_events = Column(JSON, nullable=True)  # [{"timestamp": "2025-11-28T10:30:00Z", "status": "in_transit", "location": "Montreal, QC", "description": "Package scanned at sort facility"}]
    current_location = Column(String, nullable=True)  # Latest scan location
    
    # International Shipping
    origin_country = Column(String, nullable=True)  # ISO country code (CA, US, GB)
    destination_country = Column(String, nullable=True)
    customs_declaration_url = Column(String, nullable=True)  # Commercial invoice PDF from carrier
    harmonized_codes = Column(JSON, nullable=True)  # HS codes for products [{"product_id": "123", "hs_code": "6203.42.40"}]
    duties_paid_by = Column(String, nullable=True)  # "sender" (DDP), "recipient" (DDU), "third_party"
    duties_amount_cents = Column(Integer, nullable=True)  # Customs duties in cents
    duties_currency = Column(String, nullable=True, default="USD")
    duties_paid = Column(Boolean, default=False)
    incoterms = Column(String, nullable=True)  # "DDP", "DDU", "FOB", "CIF"
    
    # Delivery Proof (from carrier)
    delivery_signature_url = Column(String, nullable=True)  # Signature image from carrier API
    delivery_photo_url = Column(String, nullable=True)  # Doorstep photo from carrier
    delivered_to_name = Column(String, nullable=True)  # Person who signed
    delivery_instructions = Column(Text, nullable=True)  # Customer's special instructions
    
    # Package Details
    weight_grams = Column(Integer, nullable=True)
    length_cm = Column(Integer, nullable=True)
    width_cm = Column(Integer, nullable=True)
    height_cm = Column(Integer, nullable=True)
    declared_value_cents = Column(Integer, nullable=True)  # For insurance
    insurance_amount_cents = Column(Integer, nullable=True)
    
    # Exception Handling
    exception_type = Column(String, nullable=True)  # "delay", "failed_delivery", "lost", "damaged", "refused", "customs_issue"
    exception_reason = Column(Text, nullable=True)  # Detailed reason from carrier
    exception_resolved = Column(Boolean, default=False)
    rescheduled_delivery = Column(DateTime, nullable=True)
    
    # Cost (what you paid the carrier)
    shipping_cost_cents = Column(Integer, nullable=True)  # What carrier charged you
    shipping_currency = Column(String, nullable=True, default="USD")
    
    # Relationships
    status_history = relationship("DeliveryStatusHistory", back_populates="delivery", cascade="all, delete-orphan")

class DeliveryStatusHistory(Base):
    __tablename__ = "delivery_status_history"
    id = Column(String, primary_key=True, default=lambda: str(UUID()))
    delivery_id = Column(String, ForeignKey("deliveries.id"), nullable=False)
    status = Column(Enum(DeliveryStatus), nullable=False)
    location = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)
    delivery = relationship("Delivery", back_populates="status_history")
