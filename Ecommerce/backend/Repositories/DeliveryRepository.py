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
