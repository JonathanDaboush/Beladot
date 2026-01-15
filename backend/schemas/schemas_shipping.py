from pydantic import BaseModel, Field
from typing import Optional

class ShipmentCreate(BaseModel):
    order_id: int
    shipment_status: Optional[str] = "created"
    shipped_at: Optional[str] = None
    delivered_at: Optional[str] = None

class ShipmentResponse(BaseModel):
    id: int
    order_id: int
    shipment_status: str
    shipped_at: Optional[str] = None
    delivered_at: Optional[str] = None

class ShipmentEventCreate(BaseModel):
    shipment_id: int
    event_type: str
    description: Optional[str] = None

class ShipmentEventResponse(BaseModel):
    id: int
    shipment_id: int
    event_type: str
    description: Optional[str] = None
