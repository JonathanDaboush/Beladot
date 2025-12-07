"""
Shipping Routes
Handles shipping carrier operations and tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import MessageResponse
from Services.ShippingCarrierService import ShippingCarrierService
from Utilities.auth import get_current_active_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/shipping", tags=["Shipping"])


@router.get("/rates", dependencies=[Depends(rate_limiter_moderate)])
async def get_shipping_rates(
    order_id: int,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get shipping rates for an order"""
    shipping_service = ShippingCarrierService(db)
    
    rates = await shipping_service.get_shipping_rates(order_id)
    
    return {"shipping_rates": rates}


@router.get("/track/{tracking_number}", dependencies=[Depends(rate_limiter_moderate)])
async def track_shipment(
    tracking_number: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Track shipment by tracking number"""
    shipping_service = ShippingCarrierService(db)
    
    tracking_info = await shipping_service.track_shipment(tracking_number)
    
    return {"tracking_info": tracking_info}
