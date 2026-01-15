from backend.persistance.db_dependency import get_db
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.schemas_shipping import (
    ShipmentCreate, ShipmentResponse, ShipmentEventCreate, ShipmentEventResponse
)
from backend.services import shippingServices

router = APIRouter(prefix="/api/v1/shipping", tags=["shipping"])

def require_role(role: str):
    async def dependency(request: Request):
        identity = getattr(request.state, "identity", {})
        if identity.get("role") not in ("employee", "seller"):
            raise HTTPException(status_code=403, detail="Forbidden")
        return identity
    return dependency

async def dummy_shipping_service():
    class DummyService:
        async def create_shipment(self, **kwargs):
            return kwargs
        async def create_shipment_event(self, **kwargs):
            return kwargs
    return DummyService()

@router.post("/shipments", response_model=ShipmentResponse)
async def create_shipment(
    shipment: ShipmentCreate,
    # shippingService dependency removed for import safety
    identity=Depends(require_role("employee")),
    db=Depends(get_db),
):
    return await shippingServices.create_shipment(employee_id=identity["employee_id"], db=db, **shipment.dict())

@router.post("/shipment-events", response_model=ShipmentEventResponse)
async def create_shipment_event(
    event: ShipmentEventCreate,
    # shippingService dependency removed for import safety
    identity=Depends(require_role("employee")),
    db=Depends(get_db),
):
    return await shippingServices.create_shipment_event(employee_id=identity["employee_id"], db=db, **event.dict())
