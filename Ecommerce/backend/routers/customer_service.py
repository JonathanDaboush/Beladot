"""
Customer Service Routes
Handles customer service operations:
- Customer inquiries and support tickets
- View/update customer information
- Schedule management (view/modify own schedule, limited 3-5 per period)
- Seller management (view/update sellers)
- User management (view/update users)
- Order management (view/update orders)
- Return confirmation (restore inventory and process refunds)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date, time
from typing import Optional, List, Dict

from database import get_db
from schemas import MessageResponse
from Services.TimeTrackingService import TimeTrackingService
from Services.SchedulingService import SchedulingService
from Services.SellerService import SellerService
from Services.UserService import UserService
from Services.OrderService import OrderService
from Utilities.auth import get_current_customer_service
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/customer-service", tags=["Customer Service"])


# ============================================================================
# TIME TRACKING
# ============================================================================

@router.post("/clock-in", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def clock_in(
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Clock in for work shift"""
    time_service = TimeTrackingService(db)
    
    await time_service.clock_in(
        employee_id=current_cs_user.id,
        clock_in_time=datetime.utcnow()
    )
    
    return {"message": "Clocked in successfully"}


@router.post("/clock-out", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def clock_out(
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Clock out from work shift"""
    time_service = TimeTrackingService(db)
    
    await time_service.clock_out(
        employee_id=current_cs_user.id,
        clock_out_time=datetime.utcnow()
    )
    
    return {"message": "Clocked out successfully"}


@router.get("/hours", dependencies=[Depends(rate_limiter_moderate)])
async def get_hours_worked(
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Get hours worked history"""
    time_service = TimeTrackingService(db)
    
    hours = await time_service.get_employee_hours(current_cs_user.id)
    
    return {"hours_worked": hours}


@router.post("/hours/manual", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def submit_manual_hours(
    work_date: date,
    regular_hours: float,
    overtime_hours: float = 0.0,
    reason: Optional[str] = None,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Submit manual hours entry (for missed clock in/out)"""
    time_service = TimeTrackingService(db)
    
    await time_service.submit_manual_hours(
        employee_id=current_cs_user.id,
        work_date=work_date,
        regular_hours=regular_hours,
        overtime_hours=overtime_hours,
        reason=reason
    )
    
    return {"message": "Manual hours submitted for approval"}


# ============================================================================
# DELIVERY TRACKING
# ============================================================================

@router.get("/orders/{order_id}/tracking", dependencies=[Depends(rate_limiter_moderate)])
async def track_customer_order(
    order_id: int,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Track delivery status for any customer order.
    Customer service can view tracking for all orders to assist customers.
    
    Shows:
    - Current delivery status
    - Tracking number and carrier
    - Estimated delivery date
    - Current location
    - Full delivery history
    - Customer information
    """
    from sqlalchemy import select
    from Models.Order import Order
    from Models.Shipment import Shipment
    from Models.User import User
    
    # Get order information
    result = await db.execute(
        select(Order, User)
        .join(User, User.id == Order.user_id)
        .where(Order.id == order_id)
    )
    order_user = result.first()
    
    if not order_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order, user = order_user
    
    # Get shipment information
    result = await db.execute(
        select(Shipment)
        .where(Shipment.order_id == order_id)
        .order_by(Shipment.created_at.desc())
    )
    shipments = result.scalars().all()
    
    if not shipments:
        return {
            "order_id": order_id,
            "order_number": order.order_number,
            "order_status": order.status.value,
            "customer_email": user.email,
            "customer_name": user.username,
            "has_shipment": False,
            "message": "No shipment created yet. Order is being processed."
        }
    
    # Format detailed tracking info
    tracking_info = []
    for shipment in shipments:
        # Parse location history from notes
        location_history = []
        if shipment.notes:
            for line in shipment.notes.split('\n'):
                if line.strip():
                    location_history.append(line.strip())
        
        tracking_info.append({
            "shipment_id": shipment.id,
            "tracking_number": shipment.tracking_number,
            "carrier": shipment.carrier,
            "status": shipment.status.value,
            "status_description": {
                "pending": "Awaiting processing",
                "picked": "Items picked from warehouse",
                "packed": "Package prepared for shipping",
                "shipped": "Package shipped",
                "in_transit": "Package is on the way",
                "out_for_delivery": "Out for delivery today",
                "delivered": "Package delivered",
                "failed": "Delivery failed"
            }.get(shipment.status.value, "Unknown status"),
            "estimated_delivery": shipment.estimated_delivery,
            "shipped_at": shipment.shipped_at,
            "delivered_at": shipment.delivered_at,
            "current_location": location_history[-1] if location_history else "Processing at warehouse",
            "location_history": location_history,
            "cost_cents": shipment.cost_cents,
            "failure_reason": shipment.failure_reason
        })
    
    return {
        "order_id": order_id,
        "order_number": order.order_number,
        "order_status": order.status.value,
        "order_created_at": order.created_at,
        "customer_email": user.email,
        "customer_name": user.username,
        "shipping_address": {
            "line1": order.shipping_line1,
            "line2": order.shipping_line2,
            "city": order.shipping_city,
            "state": order.shipping_state,
            "postal_code": order.shipping_postal_code,
            "country": order.shipping_country
        },
        "has_shipment": True,
        "shipments": tracking_info,
        "primary_tracking": tracking_info[0] if tracking_info else None
    }


@router.get("/tracking/search", dependencies=[Depends(rate_limiter_moderate)])
async def search_tracking_number(
    tracking_number: str,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for shipment by tracking number.
    Helps customer service assist customers who only have tracking number.
    """
    from sqlalchemy import select
    from Models.Shipment import Shipment
    from Models.Order import Order
    from Models.User import User
    
    # Find shipment by tracking number
    result = await db.execute(
        select(Shipment, Order, User)
        .join(Order, Order.id == Shipment.order_id)
        .join(User, User.id == Order.user_id)
        .where(Shipment.tracking_number == tracking_number)
    )
    shipment_order_user = result.first()
    
    if not shipment_order_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tracking number not found"
        )
    
    shipment, order, user = shipment_order_user
    
    # Parse location from notes
    location_history = []
    if shipment.notes:
        for line in shipment.notes.split('\n'):
            if line.strip():
                location_history.append(line.strip())
    
    return {
        "tracking_number": shipment.tracking_number,
        "carrier": shipment.carrier,
        "status": shipment.status.value,
        "estimated_delivery": shipment.estimated_delivery,
        "current_location": location_history[-1] if location_history else "In transit",
        "location_history": location_history,
        "order_id": order.id,
        "order_number": order.order_number,
        "customer_email": user.email,
        "customer_name": user.username
    }


# ============================================================================
# USER VERIFICATION
# ============================================================================

@router.get("/verify-user/{user_id}", dependencies=[Depends(rate_limiter_moderate)])
async def verify_user_account(
    user_id: int,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify customer account details.
    Used to confirm customer identity during support calls.
    
    Returns account information including:
    - Email and name
    - Account creation date
    - Email verification status
    - Account status (active/locked)
    - Recent order count
    - Last login date
    """
    from sqlalchemy import select, func
    from Models.User import User
    from Models.Order import Order
    from Models.Address import Address
    
    # Get user details
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get order count
    result = await db.execute(
        select(func.count(Order.id)).where(Order.user_id == user_id)
    )
    order_count = result.scalar() or 0
    
    # Get addresses count
    result = await db.execute(
        select(func.count(Address.id)).where(Address.user_id == user_id)
    )
    address_count = result.scalar() or 0
    
    # Get recent orders
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .limit(5)
    )
    recent_orders = result.scalars().all()
    
    return {
        "user_id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role.value,
        "account_status": {
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "is_locked": user.locked_until is not None and user.locked_until > datetime.utcnow(),
            "locked_until": user.locked_until,
            "failed_login_attempts": user.failed_login_attempts
        },
        "account_dates": {
            "created_at": user.created_at,
            "last_login": user.last_login_at,
            "updated_at": user.updated_at
        },
        "account_activity": {
            "total_orders": order_count,
            "saved_addresses": address_count,
            "recent_orders": [
                {
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "status": order.status.value,
                    "total_cents": order.total_cents,
                    "created_at": order.created_at
                }
                for order in recent_orders
            ]
        }
    }


@router.get("/verify-user-by-email", dependencies=[Depends(rate_limiter_moderate)])
async def verify_user_by_email(
    email: str,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify customer account by email address.
    Useful when customer provides email instead of account number.
    """
    from sqlalchemy import select, func
    from Models.User import User
    from Models.Order import Order
    
    # Get user by email (case-insensitive)
    result = await db.execute(
        select(User).where(User.email == email.lower())
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with that email address"
        )
    
    # Get order count
    result = await db.execute(
        select(func.count(Order.id)).where(Order.user_id == user.id)
    )
    order_count = result.scalar() or 0
    
    return {
        "user_id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role.value,
        "is_active": user.is_active,
        "email_verified": user.email_verified,
        "created_at": user.created_at,
        "last_login": user.last_login_at,
        "total_orders": order_count
    }


@router.post("/verify-identity", dependencies=[Depends(rate_limiter_moderate)])
async def verify_customer_identity(
    user_id: int,
    email: str,
    last_name: str,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify customer identity by matching multiple data points.
    Returns match status without exposing sensitive information.
    
    Used during support calls to confirm caller is the account owner.
    """
    from sqlalchemy import select
    from Models.User import User
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return {
            "verified": False,
            "message": "Account not found"
        }
    
    # Check if provided details match
    email_match = user.email.lower() == email.lower()
    last_name_match = user.last_name.lower() == last_name.lower()
    
    verified = email_match and last_name_match
    
    return {
        "verified": verified,
        "user_id": user.id if verified else None,
        "message": "Identity verified" if verified else "Information does not match our records",
        "details_matched": {
            "email": email_match,
            "last_name": last_name_match
        } if not verified else None
    }


@router.put("/hours/{hours_id}/edit", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def edit_hours(
    hours_id: int,
    regular_hours: Optional[float] = None,
    overtime_hours: Optional[float] = None,
    break_minutes: Optional[int] = None,
    notes: Optional[str] = None,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Edit existing hours entry (before approval)"""
    time_service = TimeTrackingService(db)
    
    await time_service.edit_hours(
        hours_id=hours_id,
        employee_id=current_cs_user.id,
        regular_hours=regular_hours,
        overtime_hours=overtime_hours,
        break_minutes=break_minutes,
        notes=notes
    )
    
    return {"message": "Hours updated successfully"}


@router.post("/hours/{hours_id}/break", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def add_break_time(
    hours_id: int,
    break_minutes: int,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Add break time to hours entry"""
    time_service = TimeTrackingService(db)
    
    await time_service.add_break_time(
        hours_id=hours_id,
        break_minutes=break_minutes,
        employee_id=current_cs_user.id
    )
    
    return {"message": "Break time added successfully"}


@router.get("/timesheet", dependencies=[Depends(rate_limiter_moderate)])
async def get_timesheet(
    start_date: date,
    end_date: date,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Get timesheet for date range"""
    time_service = TimeTrackingService(db)
    
    timesheet = await time_service.get_timesheet(
        employee_id=current_cs_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {"timesheet": timesheet}


# ============================================================================
# SCHEDULE MANAGEMENT
# ============================================================================

@router.get("/schedule", dependencies=[Depends(rate_limiter_moderate)])
async def view_my_schedule(
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """View own schedule"""
    scheduling_service = SchedulingService(db)
    
    schedule = await scheduling_service.get_employee_schedule(current_cs_user.id)
    
    return {"schedule": schedule}


@router.put("/schedule", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_my_schedule(
    shift_date: date,
    shift_start: time,
    shift_end: time,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Update own schedule (limited to 3-5 employees per period)"""
    scheduling_service = SchedulingService(db)
    
    # Check employee limit for the period (3-5 employees)
    scheduled_count = await scheduling_service.count_scheduled_employees(shift_date)
    
    if scheduled_count >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum of 5 employees per period reached"
        )
    
    if scheduled_count < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum of 3 employees required per period"
        )
    
    await scheduling_service.update_shift(
        employee_id=current_cs_user.id,
        shift_date=shift_date,
        shift_start=shift_start,
        shift_end=shift_end
    )
    
    return {"message": "Schedule updated successfully"}


# ============================================================================
# SELLER MANAGEMENT
# ============================================================================

@router.get("/sellers", dependencies=[Depends(rate_limiter_moderate)])
async def get_sellers(
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Get all sellers (employee access)"""
    seller_service = SellerService(db)
    
    sellers = await seller_service.get_all_sellers()
    
    return {"sellers": sellers}


@router.put("/sellers/{seller_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_seller(
    seller_id: int,
    data: dict,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Update seller information (employee access)"""
    seller_service = SellerService(db)
    
    await seller_service.update_seller(seller_id, data)
    
    return {"message": "Seller updated successfully"}


# ============================================================================
# USER MANAGEMENT
# ============================================================================

@router.get("/users", dependencies=[Depends(rate_limiter_moderate)])
async def get_users(
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Get all users (employee access)"""
    user_service = UserService(db)
    
    users = await user_service.get_all_users()
    
    return {"users": users}


@router.put("/users/{user_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_user(
    user_id: int,
    data: dict,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Update user information (employee access)"""
    user_service = UserService(db)
    
    await user_service.update_user(user_id, data)
    
    return {"message": "User updated successfully"}


# ============================================================================
# ORDER MANAGEMENT
# ============================================================================

@router.get("/orders", dependencies=[Depends(rate_limiter_moderate)])
async def view_all_orders(
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """View all customer orders"""
    order_service = OrderService(db)
    orders = await order_service.get_all_orders()
    
    return {"orders": orders}


@router.get("/orders/{order_id}", dependencies=[Depends(rate_limiter_moderate)])
async def view_order_details(
    order_id: int,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """View specific order details"""
    order_service = OrderService(db)
    order = await order_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return {"order": order}


@router.put("/orders/{order_id}/status", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_order_status(
    order_id: int,
    new_status: str,
    notes: Optional[str] = None,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Change order status (customer_service permission)"""
    order_service = OrderService(db)
    
    try:
        await order_service.update_order_status(
            order_id=order_id,
            new_status=new_status,
            actor_role='customer_service',
            notes=notes
        )
        return {"message": "Order status updated successfully"}
    except (PermissionError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# RETURN MANAGEMENT
# ============================================================================

@router.get("/returns", dependencies=[Depends(rate_limiter_moderate)])
async def view_return_requests(
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """View all return requests"""
    from sqlalchemy import select
    from Models.Return import Return, ReturnStatus
    
    result = await db.execute(
        select(Return)
        .where(Return.status == ReturnStatus.REQUESTED)
        .order_by(Return.requested_at.desc())
    )
    returns = result.scalars().all()
    
    return {"returns": returns}


@router.post("/returns/{return_id}/confirm", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def confirm_return(
    return_id: int,
    inspection_notes: Optional[str] = None,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Confirm return and restore inventory"""
    from sqlalchemy import select
    from Models.Return import Return, ReturnStatus
    from Models.Order import Order, OrderStatus
    from Services.SimpleInventoryService import SimpleInventoryService
    from Repositories.ProductRepository import ProductRepository
    from Repositories.OrderItemRepository import OrderItemRepository
    
    # Get return request
    result = await db.execute(select(Return).where(Return.id == return_id))
    return_request = result.scalar_one_or_none()
    
    if not return_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found"
        )
    
    if return_request.status != ReturnStatus.REQUESTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Return already processed"
        )
    
    # Update return status
    return_request.status = ReturnStatus.APPROVED
    if inspection_notes:
        return_request.inspection_notes = inspection_notes
    return_request.updated_at = datetime.utcnow()
    
    # Restore inventory for each returned item
    product_repo = ProductRepository(db)
    inventory_service = SimpleInventoryService(product_repo)
    order_item_repo = OrderItemRepository(db)
    
    for item_data in return_request.return_items:
        order_item_id = item_data.get('order_item_id')
        quantity = item_data.get('quantity')
        
        # Get the order item to find product_id
        order_item = await order_item_repo.get_by_id(order_item_id)
        if order_item:
            await inventory_service.restock_product(order_item.product_id, quantity)
    
    # Update order status to refunded
    order_result = await db.execute(select(Order).where(Order.id == return_request.order_id))
    order = order_result.scalar_one_or_none()
    if order:
        order.status = OrderStatus.REFUNDED
        order.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Return confirmed, inventory restored, refund processed"}


@router.post("/returns/{return_id}/reject", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def reject_return(
    return_id: int,
    rejection_reason: str,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Reject return request"""
    from sqlalchemy import select
    from Models.Return import Return, ReturnStatus
    
    result = await db.execute(select(Return).where(Return.id == return_id))
    return_request = result.scalar_one_or_none()
    
    if not return_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found"
        )
    
    if return_request.status != ReturnStatus.REQUESTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Return already processed"
        )
    
    return_request.status = ReturnStatus.REJECTED
    return_request.admin_notes = rejection_reason
    return_request.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Return request rejected"}


# ============================================================================
# USER MANAGEMENT
# ============================================================================

@router.post("/users", dependencies=[Depends(rate_limiter_moderate)])
async def create_user(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role: str = "CUSTOMER",
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user account.
    
    Customer Service can create accounts with any role.
    Password will be hashed automatically.
    """
    user_service = UserService(db)
    
    try:
        user = await user_service.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "created_at": user.created_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/users/{user_id}", dependencies=[Depends(rate_limiter_moderate)])
async def get_user_by_id(
    user_id: int,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Get user details by ID."""
    user_service = UserService(db)
    
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "created_at": user.created_at,
        "last_login": user.last_login
    }


@router.get("/users/search/by-email", dependencies=[Depends(rate_limiter_moderate)])
async def get_user_by_email(
    email: str,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """Search for user by email address."""
    user_service = UserService(db)
    
    user = await user_service.get_user_by_email(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "created_at": user.created_at,
        "last_login": user.last_login
    }


@router.put("/users/{user_id}/role", dependencies=[Depends(rate_limiter_moderate)])
async def update_user_role(
    user_id: int,
    new_role: str,
    current_cs_user=Depends(get_current_customer_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user's role.
    
    Customer Service can update any user to any role.
    """
    user_service = UserService(db)
    
    try:
        user = await user_service.update_user_role(
            user_id=user_id,
            new_role=new_role,
            admin_user_id=current_cs_user.id
        )
        
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "message": f"User role updated to {new_role}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


