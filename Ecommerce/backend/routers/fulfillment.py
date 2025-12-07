"""
Fulfillment & Shipment Tracking Routes
Handles order fulfillment operations:
- Shipment creation (automatic on confirmed purchase)
- Shipment tracking (users, shipping staff, CS, managers)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from Utilities.auth import get_current_active_user
from Utilities.rate_limiting import rate_limiter_moderate
from Models.User import UserRole

router = APIRouter(prefix="/api/shipments", tags=["Fulfillment"])


@router.get("/{shipment_id}/track", dependencies=[Depends(rate_limiter_moderate)])
async def track_shipment(
    shipment_id: int,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Track shipment status.
    
    Accessible to:
    - Customers (own orders only)
    - Shipping department employees
    - Customer service staff
    - Managers (any department)
    """
    from Services.FulfillmentService import FulfillmentService
    from sqlalchemy import select
    from Models.Shipment import Shipment
    from Models.Order import Order
    from Models.Employee import Employee
    
    fulfillment_service = FulfillmentService(db)
    
    # Get shipment
    result = await db.execute(
        select(Shipment).where(Shipment.id == shipment_id)
    )
    shipment = result.scalar_one_or_none()
    
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )
    
    # Authorization checks
    can_access = False
    
    # Check if customer owns the order
    if current_user.role == UserRole.CUSTOMER:
        result = await db.execute(
            select(Order).where(Order.id == shipment.order_id)
        )
        order = result.scalar_one_or_none()
        
        if order and order.user_id == current_user.id:
            can_access = True
    
    # Check if employee in shipping department
    elif current_user.role == UserRole.EMPLOYEE:
        result = await db.execute(
            select(Employee).where(Employee.user_id == current_user.id)
        )
        employee = result.scalar_one_or_none()
        
        if employee and employee.department == "SHIPPING":
            can_access = True
    
    # Check if CS or Manager
    elif current_user.role in [
        UserRole.CUSTOMER_SERVICE,
        UserRole.MANAGER,
        UserRole.ADMIN
    ]:
        can_access = True
    
    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to track this shipment"
        )
    
    # Get tracking info
    tracking_data = await fulfillment_service.track_shipment(
        shipment_id=shipment_id,
        actor_id=current_user.id
    )
    
    return {
        "shipment_id": shipment_id,
        "order_id": shipment.order_id,
        "tracking_number": shipment.tracking_number,
        "carrier": shipment.carrier,
        "status": tracking_data.get("status", "PENDING"),
        "estimated_delivery": tracking_data.get("estimated_delivery"),
        "tracking_events": tracking_data.get("events", []),
        "last_updated": tracking_data.get("last_updated")
    }


@router.get("/order/{order_id}", dependencies=[Depends(rate_limiter_moderate)])
async def get_order_shipments(
    order_id: int,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all shipments for an order.
    
    Customers can view own orders, staff can view any.
    """
    from sqlalchemy import select
    from Models.Shipment import Shipment
    from Models.Order import Order
    from Models.Employee import Employee
    
    # Get order
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Authorization
    can_access = False
    
    if current_user.role == UserRole.CUSTOMER and order.user_id == current_user.id:
        can_access = True
    elif current_user.role == UserRole.EMPLOYEE:
        result = await db.execute(
            select(Employee).where(Employee.user_id == current_user.id)
        )
        employee = result.scalar_one_or_none()
        if employee and employee.department == "SHIPPING":
            can_access = True
    elif current_user.role in [
        UserRole.CUSTOMER_SERVICE,
        UserRole.MANAGER,
        UserRole.ADMIN
    ]:
        can_access = True
    
    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view these shipments"
        )
    
    # Get shipments
    result = await db.execute(
        select(Shipment).where(Shipment.order_id == order_id)
    )
    shipments = result.scalars().all()
    
    return {
        "order_id": order_id,
        "shipments": [
            {
                "id": s.id,
                "tracking_number": s.tracking_number,
                "carrier": s.carrier,
                "status": s.status,
                "shipped_at": s.shipped_at.isoformat() if s.shipped_at else None,
                "estimated_delivery": s.estimated_delivery.isoformat() if s.estimated_delivery else None
            }
            for s in shipments
        ]
    }
