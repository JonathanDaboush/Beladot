from pydantic import BaseModel, Field
from typing import Optional, Literal

class ShipmentCreate(BaseModel):
    order_id: int = Field(..., gt=0)
    shipment_status: Optional[Literal["created","in_transit","delivered","cancelled"]] = "created"
    shipped_at: Optional[str] = None
    delivered_at: Optional[str] = None

class ShipmentResponse(BaseModel):
    id: int
    order_id: int
    shipment_status: Literal["created","in_transit","delivered","cancelled"]
    shipped_at: Optional[str] = None
    delivered_at: Optional[str] = None

class ShipmentEventCreate(BaseModel):
    shipment_id: int = Field(..., gt=0)
    event_type: Literal["picked_up","scanned","out_for_delivery","delivered","issue"]
    description: Optional[str] = Field(default=None, min_length=1, max_length=500)

class ShipmentEventResponse(BaseModel):
    id: int
    shipment_id: int
    event_type: Literal["picked_up","scanned","out_for_delivery","delivered","issue"]
    description: Optional[str] = None
