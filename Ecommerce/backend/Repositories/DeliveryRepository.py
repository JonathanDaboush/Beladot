from Ecommerce.backend.Models.Delivery import Delivery, DeliveryStatusHistory, DeliveryStatus, DeliveryType
from Ecommerce.backend.database import get_db
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from datetime import datetime

class DeliveryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_delivery(self, **kwargs) -> Delivery:
        delivery = Delivery(**kwargs)
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def get_by_id(self, delivery_id: str) -> Optional[Delivery]:
        return self.db.query(Delivery).filter(Delivery.id == delivery_id).first()

    def update_status(self, delivery_id: str, status: DeliveryStatus, location: Optional[str] = None, notes: Optional[str] = None) -> DeliveryStatusHistory:
        delivery = self.get_by_id(delivery_id)
        if not delivery:
            raise ValueError("Delivery not found")
        delivery.status = status
        delivery.updated_at = datetime.utcnow()
        status_history = DeliveryStatusHistory(
            delivery_id=delivery_id,
            status=status,
            location=location,
            notes=notes
        )
        self.db.add(status_history)
        self.db.commit()
        self.db.refresh(status_history)
        self.db.refresh(delivery)
        return status_history

    def get_status_history(self, delivery_id: str) -> List[DeliveryStatusHistory]:
        return self.db.query(DeliveryStatusHistory).filter(DeliveryStatusHistory.delivery_id == delivery_id).order_by(DeliveryStatusHistory.timestamp).all()

    def get_by_tracking_number(self, tracking_number: str) -> Optional[Delivery]:
        """Find delivery by carrier tracking number (for webhook lookups)."""
        return self.db.query(Delivery).filter(Delivery.tracking_number == tracking_number).first()

    def get_in_transit_deliveries(self) -> List[Delivery]:
        """Get all active deliveries that need tracking updates (for polling job)."""
        active_statuses = [
            DeliveryStatus.picked_up,
            DeliveryStatus.in_transit,
            DeliveryStatus.out_for_delivery,
            DeliveryStatus.customs_hold
        ]
        return self.db.query(Delivery).filter(Delivery.status.in_(active_statuses)).all()

    def update_tracking_info(self, delivery_id: str, tracking_data: dict) -> Delivery:
        """Update delivery with carrier tracking data."""
        delivery = self.get_by_id(delivery_id)
        if not delivery:
            raise ValueError("Delivery not found")
        
        # Update tracking events (append new events)
        if tracking_data.get("events"):
            existing_events = delivery.tracking_events or []
            existing_events.extend(tracking_data["events"])
            delivery.tracking_events = existing_events
        
        # Update current status and location
        if tracking_data.get("status"):
            delivery.status = tracking_data["status"]
        if tracking_data.get("current_location"):
            delivery.current_location = tracking_data["current_location"]
        if tracking_data.get("estimated_delivery"):
            delivery.estimated_delivery = tracking_data["estimated_delivery"]
        
        delivery.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def mark_delivered(self, delivery_id: str, delivered_at: datetime, signature_url: str = None, photo_url: str = None, delivered_to: str = None) -> Delivery:
        """Mark delivery as complete with proof."""
        delivery = self.get_by_id(delivery_id)
        if not delivery:
            raise ValueError("Delivery not found")
        
        delivery.status = DeliveryStatus.delivered
        delivery.actual_delivery = delivered_at
        delivery.delivery_signature_url = signature_url
        delivery.delivery_photo_url = photo_url
        delivery.delivered_to_name = delivered_to
        delivery.updated_at = datetime.utcnow()
        
        # Add to status history
        status_history = DeliveryStatusHistory(
            delivery_id=delivery_id,
            status=DeliveryStatus.delivered,
            timestamp=delivered_at,
            notes=f"Delivered to {delivered_to}" if delivered_to else "Delivered"
        )
        self.db.add(status_history)
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def record_exception(self, delivery_id: str, exception_type: str, reason: str) -> Delivery:
        """Record delivery exception (delay, failed attempt, lost, etc.)."""
        delivery = self.get_by_id(delivery_id)
        if not delivery:
            raise ValueError("Delivery not found")
        
        delivery.status = DeliveryStatus.exception
        delivery.exception_type = exception_type
        delivery.exception_reason = reason
        delivery.updated_at = datetime.utcnow()
        
        status_history = DeliveryStatusHistory(
            delivery_id=delivery_id,
            status=DeliveryStatus.exception,
            notes=f"{exception_type}: {reason}"
        )
        self.db.add(status_history)
        self.db.commit()
        self.db.refresh(delivery)
        return delivery
