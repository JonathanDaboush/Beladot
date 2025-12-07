"""
Manager Router
Handles manager approval workflows for time tracking, scheduling, and leave requests
Manager role has department-based approval scope
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date, timedelta
from typing import Optional, List

from database import get_db
from Utilities.auth import get_current_user
from Utilities.rate_limiting import rate_limiter_moderate
from Models.User import UserRole

router = APIRouter(prefix="/api/manager", tags=["Manager"])


def require_manager(current_user=Depends(get_current_user)):
    """Verify user has MANAGER role"""
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager role required"
        )
    return current_user


async def get_manager_employee(current_user, db: AsyncSession):
    """Get manager's employee record"""
    from sqlalchemy import select
    from Models.Employee import Employee
    
    result = await db.execute(
        select(Employee).where(Employee.email == current_user.email)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager employee record not found"
        )
    
    return employee


# ===== TIME TRACKING APPROVALS =====

@router.get("/time-tracking/pending", dependencies=[Depends(rate_limiter_moderate)])
async def get_pending_time_entries(
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Get pending time tracking entries for manager's department.
    
    Manager can only approve entries for employees in their department.
    """
    manager_employee = await get_manager_employee(current_user, db)
    
    from sqlalchemy import select
    from Models.HoursWorked import HoursWorked
    from Models.Employee import Employee
    
    # Get pending entries for manager's department
    result = await db.execute(
        select(HoursWorked, Employee)
        .join(Employee, Employee.id == HoursWorked.employee_id)
        .where(Employee.department == manager_employee.department)
        .where(HoursWorked.approved == False)
        .order_by(HoursWorked.work_date.desc())
    )
    
    entries = []
    for hours, employee in result.all():
        entries.append({
            "id": hours.id,
            "employee_id": employee.id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "employee_number": employee.employee_number,
            "work_date": hours.work_date,
            "clock_in": hours.clock_in,
            "clock_out": hours.clock_out,
            "total_hours": hours.total_hours,
            "break_minutes": hours.break_minutes
        })
    
    return {
        "department": manager_employee.department,
        "pending_entries": entries,
        "count": len(entries)
    }


@router.get("/orders/tracking-overview", dependencies=[Depends(rate_limiter_moderate)])
async def get_delivery_tracking_overview(
    status: Optional[str] = None,
    carrier: Optional[str] = None,
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Get overview of all shipments and delivery status.
    Manager can monitor all deliveries to ensure customer satisfaction.
    """
    from sqlalchemy import select
    from Models.Shipment import Shipment, ShipmentStatus
    from Models.Order import Order
    
    # Build query
    query = select(Shipment, Order).join(Order, Order.id == Shipment.order_id)
    
    # Filter by status if specified
    if status:
        try:
            status_enum = ShipmentStatus(status)
            query = query.where(Shipment.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )
    
    # Filter by carrier if specified
    if carrier:
        query = query.where(Shipment.carrier == carrier)
    
    # Order by most recent first
    query = query.order_by(Shipment.created_at.desc()).limit(100)
    
    result = await db.execute(query)
    shipment_order_pairs = result.all()
    
    # Format results
    shipments_summary = []
    for shipment, order in shipment_order_pairs:
        # Parse current location from notes
        current_location = "Processing"
        if shipment.notes:
            locations = [line.strip() for line in shipment.notes.split('\n') if line.strip()]
            if locations:
                current_location = locations[-1]
        
        shipments_summary.append({
            "shipment_id": shipment.id,
            "order_id": order.id,
            "order_number": order.order_number,
            "tracking_number": shipment.tracking_number,
            "carrier": shipment.carrier,
            "status": shipment.status.value,
            "current_location": current_location,
            "estimated_delivery": shipment.estimated_delivery,
            "shipped_at": shipment.shipped_at,
            "delivered_at": shipment.delivered_at,
            "customer_city": order.shipping_city,
            "customer_state": order.shipping_state
        })
    
    # Calculate statistics
    from collections import Counter
    status_counts = Counter(s["status"] for s in shipments_summary)
    carrier_counts = Counter(s["carrier"] for s in shipments_summary)
    
    return {
        "total_shipments": len(shipments_summary),
        "shipments": shipments_summary,
        "statistics": {
            "by_status": dict(status_counts),
            "by_carrier": dict(carrier_counts)
        }
    }


@router.get("/orders/{order_id}/tracking", dependencies=[Depends(rate_limiter_moderate)])
async def track_order_as_manager(
    order_id: int,
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Track specific order delivery status.
    Manager can view detailed tracking to assist with customer inquiries.
    """
    from sqlalchemy import select
    from Models.Order import Order
    from Models.Shipment import Shipment
    from Models.User import User
    
    # Get order with customer info
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
    
    # Get all shipments for this order
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
            "has_shipment": False,
            "message": "No shipment created yet"
        }
    
    # Format tracking details
    tracking_details = []
    for shipment in shipments:
        location_history = []
        if shipment.notes:
            location_history = [line.strip() for line in shipment.notes.split('\n') if line.strip()]
        
        tracking_details.append({
            "shipment_id": shipment.id,
            "tracking_number": shipment.tracking_number,
            "carrier": shipment.carrier,
            "status": shipment.status.value,
            "estimated_delivery": shipment.estimated_delivery,
            "shipped_at": shipment.shipped_at,
            "delivered_at": shipment.delivered_at,
            "current_location": location_history[-1] if location_history else "In transit",
            "location_history": location_history,
            "cost_cents": shipment.cost_cents
        })
    
    return {
        "order_id": order_id,
        "order_number": order.order_number,
        "order_status": order.status.value,
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
        "shipments": tracking_details
    }


# ============================================================================
# USER VERIFICATION
# ============================================================================

@router.get("/verify-user/{user_id}", dependencies=[Depends(rate_limiter_moderate)])
async def verify_user_account(
    user_id: int,
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify customer account details.
    Manager can view customer account information for verification purposes.
    """
    from sqlalchemy import select, func
    from Models.User import User
    from Models.Order import Order
    from Models.Address import Address
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get order statistics
    result = await db.execute(
        select(func.count(Order.id)).where(Order.user_id == user_id)
    )
    order_count = result.scalar() or 0
    
    # Get total spent
    result = await db.execute(
        select(func.sum(Order.total_cents)).where(Order.user_id == user_id)
    )
    total_spent_cents = result.scalar() or 0
    
    # Get addresses
    result = await db.execute(
        select(Address).where(Address.user_id == user_id)
    )
    addresses = result.scalars().all()
    
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
            "locked_until": user.locked_until
        },
        "account_dates": {
            "created_at": user.created_at,
            "last_login": user.last_login_at
        },
        "account_statistics": {
            "total_orders": order_count,
            "total_spent_cents": int(total_spent_cents),
            "saved_addresses": len(addresses)
        },
        "addresses": [
            {
                "id": addr.id,
                "line1": addr.line1,
                "line2": addr.line2,
                "city": addr.city,
                "state": addr.state,
                "postal_code": addr.postal_code,
                "country": addr.country,
                "is_default": addr.is_default
            }
            for addr in addresses
        ]
    }


@router.get("/verify-user-by-email", dependencies=[Depends(rate_limiter_moderate)])
async def verify_user_by_email(
    email: str,
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Look up customer account by email address.
    """
    from sqlalchemy import select, func
    from Models.User import User
    from Models.Order import Order
    
    result = await db.execute(
        select(User).where(User.email == email.lower())
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
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
        "total_orders": order_count
    }


@router.post("/time-tracking/{entry_id}/approve", dependencies=[Depends(rate_limiter_moderate)])
async def approve_time_entry(
    entry_id: int,
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """Approve time tracking entry (department-scoped)"""
    manager_employee = await get_manager_employee(current_user, db)
    
    from sqlalchemy import select
    from Models.HoursWorked import HoursWorked
    from Models.Employee import Employee
    
    # Get entry with employee
    result = await db.execute(
        select(HoursWorked, Employee)
        .join(Employee, Employee.id == HoursWorked.employee_id)
        .where(HoursWorked.id == entry_id)
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )
    
    hours, employee = row
    
    # Verify same department
    if employee.department != manager_employee.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot approve entries outside your department ({manager_employee.department})"
        )
    
    # Approve
    hours.approved = True
    await db.commit()
    
    return {
        "entry_id": entry_id,
        "employee": f"{employee.first_name} {employee.last_name}",
        "work_date": hours.work_date,
        "total_hours": hours.total_hours,
        "message": "Time entry approved successfully"
    }


# ===== SCHEDULE APPROVALS =====

@router.get("/schedules/pending", dependencies=[Depends(rate_limiter_moderate)])
async def get_pending_schedules(
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Get pending schedule requests for manager's department.
    
    Shows employee availability submissions awaiting approval.
    """
    manager_employee = await get_manager_employee(current_user, db)
    
    from sqlalchemy import select
    from Models.EmployeeSchedule import EmployeeSchedule
    from Models.Employee import Employee
    
    result = await db.execute(
        select(EmployeeSchedule, Employee)
        .join(Employee, Employee.id == EmployeeSchedule.employee_id)
        .where(Employee.department == manager_employee.department)
        .where(EmployeeSchedule.approved == False)
        .where(EmployeeSchedule.schedule_date >= date.today())
        .order_by(EmployeeSchedule.schedule_date)
    )
    
    schedules = []
    for schedule, employee in result.all():
        schedules.append({
            "id": schedule.id,
            "employee_id": employee.id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "employee_number": employee.employee_number,
            "schedule_date": schedule.schedule_date,
            "start_time": schedule.start_time,
            "end_time": schedule.end_time,
            "is_available": schedule.is_available
        })
    
    return {
        "department": manager_employee.department,
        "pending_schedules": schedules,
        "count": len(schedules)
    }


@router.post("/schedules/{schedule_id}/approve", dependencies=[Depends(rate_limiter_moderate)])
async def approve_schedule(
    schedule_id: int,
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """Approve employee schedule/availability (department-scoped)"""
    manager_employee = await get_manager_employee(current_user, db)
    
    from sqlalchemy import select
    from Models.EmployeeSchedule import EmployeeSchedule
    from Models.Employee import Employee
    
    result = await db.execute(
        select(EmployeeSchedule, Employee)
        .join(Employee, Employee.id == EmployeeSchedule.employee_id)
        .where(EmployeeSchedule.id == schedule_id)
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    schedule, employee = row
    
    # Verify same department
    if employee.department != manager_employee.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot approve schedules outside your department ({manager_employee.department})"
        )
    
    # Approve
    schedule.approved = True
    await db.commit()
    
    return {
        "schedule_id": schedule_id,
        "employee": f"{employee.first_name} {employee.last_name}",
        "schedule_date": schedule.schedule_date,
        "is_available": schedule.is_available,
        "message": "Schedule approved successfully"
    }


# ===== LEAVE APPROVALS =====

@router.get("/leave/pending", dependencies=[Depends(rate_limiter_moderate)])
async def get_pending_leave_requests(
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Get pending PTO and sick leave requests for manager's department.
    """
    manager_employee = await get_manager_employee(current_user, db)
    
    from sqlalchemy import select
    from Models.PaidTimeOff import PaidTimeOff
    from Models.PaidSick import PaidSick
    from Models.Employee import Employee
    
    # Get pending PTO
    pto_result = await db.execute(
        select(PaidTimeOff, Employee)
        .join(Employee, Employee.id == PaidTimeOff.employee_id)
        .where(Employee.department == manager_employee.department)
        .where(PaidTimeOff.approved == False)
        .order_by(PaidTimeOff.date_used.desc())
    )
    
    # Get pending sick leave
    sick_result = await db.execute(
        select(PaidSick, Employee)
        .join(Employee, Employee.id == PaidSick.employee_id)
        .where(Employee.department == manager_employee.department)
        .where(PaidSick.approved == False)
        .order_by(PaidSick.date_used.desc())
    )
    
    pto_requests = []
    for pto, employee in pto_result.all():
        pto_requests.append({
            "id": pto.id,
            "type": "PTO",
            "employee_id": employee.id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "employee_number": employee.employee_number,
            "date_used": pto.date_used,
            "hours": pto.hours
        })
    
    sick_requests = []
    for sick, employee in sick_result.all():
        sick_requests.append({
            "id": sick.id,
            "type": "Sick",
            "employee_id": employee.id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "employee_number": employee.employee_number,
            "date_used": sick.date_used,
            "hours": sick.hours
        })
    
    return {
        "department": manager_employee.department,
        "pto_requests": pto_requests,
        "sick_requests": sick_requests,
        "total_pending": len(pto_requests) + len(sick_requests)
    }


@router.post("/leave/pto/{pto_id}/approve", dependencies=[Depends(rate_limiter_moderate)])
async def approve_pto_request(
    pto_id: int,
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """Approve PTO request (department-scoped)"""
    manager_employee = await get_manager_employee(current_user, db)
    
    from sqlalchemy import select
    from Models.PaidTimeOff import PaidTimeOff
    from Models.Employee import Employee
    
    result = await db.execute(
        select(PaidTimeOff, Employee)
        .join(Employee, Employee.id == PaidTimeOff.employee_id)
        .where(PaidTimeOff.id == pto_id)
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PTO request not found"
        )
    
    pto, employee = row
    
    if employee.department != manager_employee.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot approve leave outside your department ({manager_employee.department})"
        )
    
    pto.approved = True
    await db.commit()
    
    return {
        "pto_id": pto_id,
        "employee": f"{employee.first_name} {employee.last_name}",
        "date_used": pto.date_used,
        "hours": pto.hours,
        "message": "PTO request approved successfully"
    }


@router.post("/leave/sick/{sick_id}/approve", dependencies=[Depends(rate_limiter_moderate)])
async def approve_sick_leave_request(
    sick_id: int,
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """Approve sick leave request (department-scoped)"""
    manager_employee = await get_manager_employee(current_user, db)
    
    from sqlalchemy import select
    from Models.PaidSick import PaidSick
    from Models.Employee import Employee
    
    result = await db.execute(
        select(PaidSick, Employee)
        .join(Employee, Employee.id == PaidSick.employee_id)
        .where(PaidSick.id == sick_id)
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sick leave request not found"
        )
    
    sick, employee = row
    
    if employee.department != manager_employee.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot approve leave outside your department ({manager_employee.department})"
        )
    
    sick.approved = True
    await db.commit()
    
    return {
        "sick_id": sick_id,
        "employee": f"{employee.first_name} {employee.last_name}",
        "date_used": sick.date_used,
        "hours": sick.hours,
        "message": "Sick leave request approved successfully"
    }


# ===== DEPARTMENT OVERVIEW =====

@router.get("/department/overview", dependencies=[Depends(rate_limiter_moderate)])
async def get_department_overview(
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Get overview of manager's department:
    - Total employees
    - Pending approvals (time, schedule, leave)
    - Today's availability
    """
    manager_employee = await get_manager_employee(current_user, db)
    
    from sqlalchemy import select, func
    from Models.Employee import Employee
    from Models.HoursWorked import HoursWorked
    from Models.EmployeeSchedule import EmployeeSchedule
    from Models.PaidTimeOff import PaidTimeOff
    from Models.PaidSick import PaidSick
    
    # Total employees in department
    result = await db.execute(
        select(func.count(Employee.id))
        .where(Employee.department == manager_employee.department)
        .where(Employee.is_active == True)
    )
    total_employees = result.scalar()
    
    # Pending time entries
    result = await db.execute(
        select(func.count(HoursWorked.id))
        .join(Employee, Employee.id == HoursWorked.employee_id)
        .where(Employee.department == manager_employee.department)
        .where(HoursWorked.approved == False)
    )
    pending_time = result.scalar()
    
    # Pending schedules
    result = await db.execute(
        select(func.count(EmployeeSchedule.id))
        .join(Employee, Employee.id == EmployeeSchedule.employee_id)
        .where(Employee.department == manager_employee.department)
        .where(EmployeeSchedule.approved == False)
    )
    pending_schedules = result.scalar()
    
    # Pending PTO
    result = await db.execute(
        select(func.count(PaidTimeOff.id))
        .join(Employee, Employee.id == PaidTimeOff.employee_id)
        .where(Employee.department == manager_employee.department)
        .where(PaidTimeOff.approved == False)
    )
    pending_pto = result.scalar()
    
    # Pending sick leave
    result = await db.execute(
        select(func.count(PaidSick.id))
        .join(Employee, Employee.id == PaidSick.employee_id)
        .where(Employee.department == manager_employee.department)
        .where(PaidSick.approved == False)
    )
    pending_sick = result.scalar()
    
    # Today's availability
    today = date.today()
    result = await db.execute(
        select(func.count(EmployeeSchedule.id))
        .join(Employee, Employee.id == EmployeeSchedule.employee_id)
        .where(Employee.department == manager_employee.department)
        .where(EmployeeSchedule.schedule_date == today)
        .where(EmployeeSchedule.is_available == True)
        .where(EmployeeSchedule.approved == True)
    )
    available_today = result.scalar()
    
    return {
        "department": manager_employee.department,
        "manager": f"{manager_employee.first_name} {manager_employee.last_name}",
        "total_employees": total_employees,
        "available_today": available_today,
        "pending_approvals": {
            "time_entries": pending_time,
            "schedules": pending_schedules,
            "pto": pending_pto,
            "sick_leave": pending_sick,
            "total": pending_time + pending_schedules + pending_pto + pending_sick
        }
    }


@router.put("/hours/{hours_id}", dependencies=[Depends(rate_limiter_moderate)])
async def edit_hours_entry(
    hours_id: int,
    clock_in: Optional[datetime] = None,
    clock_out: Optional[datetime] = None,
    work_date: Optional[date] = None,
    break_minutes: Optional[int] = None,
    notes: Optional[str] = None,
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Manager edits hours entry for employee in their department.
    
    Manager can modify:
    - Clock in/out times
    - Work date
    - Break minutes
    - Notes
    
    Hours are automatically recalculated.
    Department scope enforced.
    """
    manager_employee = await get_manager_employee(current_user, db)
    
    from sqlalchemy import select
    from Models.HoursWorked import HoursWorked
    from Models.Employee import Employee
    from Services.TimeTrackingService import TimeTrackingService
    
    # Get hours entry with employee info
    result = await db.execute(
        select(HoursWorked, Employee)
        .join(Employee, Employee.id == HoursWorked.employee_id)
        .where(HoursWorked.id == hours_id)
    )
    
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hours entry not found"
        )
    
    hours, employee = row
    
    # Verify department scope
    if employee.department != manager_employee.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot edit hours for employee outside your department. Employee is in {employee.department}, you manage {manager_employee.department}"
        )
    
    time_service = TimeTrackingService(db)
    
    # Build update data
    update_data = {}
    if clock_in is not None:
        update_data["clock_in"] = clock_in
    if clock_out is not None:
        update_data["clock_out"] = clock_out
    if work_date is not None:
        update_data["work_date"] = work_date
    if break_minutes is not None:
        update_data["break_minutes"] = break_minutes
    if notes is not None:
        update_data["notes"] = notes
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    try:
        updated_hours = await time_service.edit_hours(
            hours_id=hours_id,
            manager_id=manager_employee.id,
            **update_data
        )
        
        return {
            "message": "Hours entry updated successfully",
            "hours_id": updated_hours.id,
            "employee_id": updated_hours.employee_id,
            "work_date": updated_hours.work_date,
            "clock_in": updated_hours.clock_in,
            "clock_out": updated_hours.clock_out,
            "total_hours": float(updated_hours.hours_worked or 0),
            "regular_hours": float(updated_hours.regular_hours or 0),
            "overtime_hours": float(updated_hours.overtime_hours or 0),
            "edited_by": f"{manager_employee.first_name} {manager_employee.last_name}",
            "edited_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/shifts/bulk", dependencies=[Depends(rate_limiter_moderate)])
async def bulk_create_shifts(
    shifts: List[dict],
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk create multiple shifts at once.
    
    Manager can create shifts for employees in their department.
    Useful for creating weekly schedules.
    """
    manager_employee = await get_manager_employee(current_user, db)
    
    from Services.SchedulingService import SchedulingService
    
    scheduling_service = SchedulingService(db)
    
    try:
        created_shifts = await scheduling_service.bulk_create_shifts(
            shifts=shifts,
            created_by=manager_employee.id,
            department=manager_employee.department
        )
        
        return {
            "message": f"Created {len(created_shifts)} shifts successfully",
            "shifts": [
                {
                    "id": shift.id,
                    "employee_id": shift.employee_id,
                    "shift_date": shift.shift_date,
                    "shift_start": shift.shift_start,
                    "shift_end": shift.shift_end
                }
                for shift in created_shifts
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/shifts/recurring", dependencies=[Depends(rate_limiter_moderate)])
async def create_recurring_shifts(
    employee_id: int,
    start_date: date,
    end_date: date,
    shift_start: str,
    shift_end: str,
    days_of_week: List[int],
    position: Optional[str] = None,
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Create recurring shift pattern for an employee.
    
    Args:
        days_of_week: List of weekday numbers (0=Monday, 6=Sunday)
        
    Example: Create Mon/Wed/Fri shifts for a month
    """
    manager_employee = await get_manager_employee(current_user, db)
    
    from Services.SchedulingService import SchedulingService
    from datetime import time as time_type
    
    # Verify employee in manager's department
    from sqlalchemy import select
    from Models.Employee import Employee
    
    result = await db.execute(
        select(Employee).where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    if employee.department != manager_employee.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee not in your department"
        )
    
    scheduling_service = SchedulingService(db)
    
    # Parse time strings
    from datetime import datetime
    start_time = datetime.strptime(shift_start, "%H:%M").time()
    end_time = datetime.strptime(shift_end, "%H:%M").time()
    
    try:
        created_shifts = await scheduling_service.create_recurring_shifts(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            shift_start=start_time,
            shift_end=end_time,
            days_of_week=days_of_week,
            position=position or employee.position,
            department=employee.department,
            location=employee.location,
            created_by=manager_employee.id
        )
        
        return {
            "message": f"Created {len(created_shifts)} recurring shifts",
            "pattern": {
                "employee_id": employee_id,
                "days": days_of_week,
                "time": f"{shift_start} - {shift_end}"
            },
            "shifts_created": len(created_shifts)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/shifts/{shift_id}", dependencies=[Depends(rate_limiter_moderate)])
async def cancel_shift(
    shift_id: int,
    reason: Optional[str] = None,
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a scheduled shift.
    
    Manager can only cancel shifts in their department.
    """
    manager_employee = await get_manager_employee(current_user, db)
    
    from sqlalchemy import select
    from Models.EmployeeSchedule import EmployeeSchedule
    from Models.Employee import Employee
    from Services.SchedulingService import SchedulingService
    
    # Get shift with employee info
    result = await db.execute(
        select(EmployeeSchedule, Employee)
        .join(Employee, Employee.id == EmployeeSchedule.employee_id)
        .where(EmployeeSchedule.id == shift_id)
    )
    
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )
    
    shift, employee = row
    
    # Verify department scope
    if employee.department != manager_employee.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Shift not in your department"
        )
    
    scheduling_service = SchedulingService(db)
    
    try:
        await scheduling_service.cancel_shift(
            shift_id=shift_id,
            cancelled_by=manager_employee.id,
            reason=reason
        )
        
        return {
            "message": "Shift cancelled successfully",
            "shift_id": shift_id,
            "employee_id": employee.id,
            "shift_date": shift.shift_date,
            "reason": reason
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/shifts/{shift_id}/time", dependencies=[Depends(rate_limiter_moderate)])
async def update_shift_time(
    shift_id: int,
    shift_start: Optional[str] = None,
    shift_end: Optional[str] = None,
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Update shift start/end times.
    
    Manager can only update shifts in their department.
    """
    manager_employee = await get_manager_employee(current_user, db)
    
    from sqlalchemy import select
    from Models.EmployeeSchedule import EmployeeSchedule
    from Models.Employee import Employee
    from Services.SchedulingService import SchedulingService
    from datetime import datetime
    
    # Get shift with employee info
    result = await db.execute(
        select(EmployeeSchedule, Employee)
        .join(Employee, Employee.id == EmployeeSchedule.employee_id)
        .where(EmployeeSchedule.id == shift_id)
    )
    
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )
    
    shift, employee = row
    
    # Verify department scope
    if employee.department != manager_employee.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Shift not in your department"
        )
    
    # Parse times
    start_time = None
    end_time = None
    
    if shift_start:
        start_time = datetime.strptime(shift_start, "%H:%M").time()
    if shift_end:
        end_time = datetime.strptime(shift_end, "%H:%M").time()
    
    scheduling_service = SchedulingService(db)
    
    try:
        updated_shift = await scheduling_service.update_shift_time(
            shift_id=shift_id,
            new_start=start_time,
            new_end=end_time,
            updated_by=manager_employee.id
        )
        
        return {
            "message": "Shift times updated successfully",
            "shift_id": shift_id,
            "employee_id": employee.id,
            "shift_date": updated_shift.shift_date,
            "new_start": updated_shift.shift_start,
            "new_end": updated_shift.shift_end,
            "calculated_hours": updated_shift.calculate_shift_hours()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# USER MANAGEMENT (Department-Scoped)
# ============================================================================

@router.post("/users", dependencies=[Depends(rate_limiter_moderate)])
async def create_user_in_department(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role: str = "EMPLOYEE",
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user account (Manager, department-scoped).
    
    Manager can only create EMPLOYEE or CUSTOMER_SERVICE roles
    and they will be assigned to manager's department.
    """
    from Services.UserService import UserService
    from Models.User import UserRole
    
    # Verify manager's employee record
    manager_employee = await get_manager_employee(current_user, db)
    
    # Managers can only create EMPLOYEE or CUSTOMER_SERVICE roles
    allowed_roles = [UserRole.EMPLOYEE.value, UserRole.CUSTOMER_SERVICE.value]
    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Managers can only create EMPLOYEE or CUSTOMER_SERVICE roles"
        )
    
    user_service = UserService(db)
    
    try:
        user = await user_service.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        # If creating an employee, assign to manager's department
        if role == UserRole.EMPLOYEE.value:
            from sqlalchemy import select
            from Models.Employee import Employee
            
            # Create employee record with department assignment
            new_employee = Employee(
                user_id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                department=manager_employee.department,
                employee_number=f"EMP{user.id:06d}"
            )
            db.add(new_employee)
            await db.commit()
        
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "department": manager_employee.department if role == UserRole.EMPLOYEE.value else None,
            "created_at": user.created_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/users/{user_id}", dependencies=[Depends(rate_limiter_moderate)])
async def get_user_by_id_in_department(
    user_id: int,
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user details by ID (Manager, department-scoped).
    
    Manager can only view users in their department.
    """
    from Services.UserService import UserService
    from sqlalchemy import select
    from Models.Employee import Employee
    
    manager_employee = await get_manager_employee(current_user, db)
    user_service = UserService(db)
    
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is an employee in manager's department
    result = await db.execute(
        select(Employee).where(Employee.user_id == user_id)
    )
    employee = result.scalar_one_or_none()
    
    if employee and employee.department != manager_employee.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized - user not in your department"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "department": employee.department if employee else None,
        "created_at": user.created_at,
        "last_login": user.last_login_at
    }


@router.get("/users/search/by-email", dependencies=[Depends(rate_limiter_moderate)])
async def get_user_by_email_in_department(
    email: str,
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for user by email (Manager, department-scoped).
    
    Manager can only view users in their department.
    """
    from Services.UserService import UserService
    from sqlalchemy import select
    from Models.Employee import Employee
    
    manager_employee = await get_manager_employee(current_user, db)
    user_service = UserService(db)
    
    user = await user_service.get_user_by_email(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is an employee in manager's department
    result = await db.execute(
        select(Employee).where(Employee.user_id == user.id)
    )
    employee = result.scalar_one_or_none()
    
    if employee and employee.department != manager_employee.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized - user not in your department"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "department": employee.department if employee else None,
        "created_at": user.created_at,
        "last_login": user.last_login_at
    }


@router.put("/users/{user_id}/role", dependencies=[Depends(rate_limiter_moderate)])
async def update_user_role_in_department(
    user_id: int,
    new_role: str,
    current_user=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user's role (Manager, department-scoped).
    
    Manager can only update roles for users in their department.
    Can only assign EMPLOYEE or CUSTOMER_SERVICE roles.
    """
    from Services.UserService import UserService
    from sqlalchemy import select
    from Models.Employee import Employee
    from Models.User import UserRole
    
    manager_employee = await get_manager_employee(current_user, db)
    
    # Managers can only assign EMPLOYEE or CUSTOMER_SERVICE roles
    allowed_roles = [UserRole.EMPLOYEE.value, UserRole.CUSTOMER_SERVICE.value]
    if new_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only assign EMPLOYEE or CUSTOMER_SERVICE roles"
        )
    
    # Check if user is in manager's department
    result = await db.execute(
        select(Employee).where(Employee.user_id == user_id)
    )
    employee = result.scalar_one_or_none()
    
    if employee and employee.department != manager_employee.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized - user not in your department"
        )
    
    user_service = UserService(db)
    
    try:
        user = await user_service.update_user_role(
            user_id=user_id,
            new_role=new_role,
            admin_user_id=current_user.id
        )
        
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "department": employee.department if employee else None,
            "message": f"User role updated to {new_role}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )



# ===== USER MANAGEMENT (DEPARTMENT-SCOPED) =====

@router.post("/users", dependencies=[Depends(rate_limiter_moderate)])
async def create_user(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role: str = "EMPLOYEE",
    department: str = None,
    manager=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user account (department-scoped).
    
    Managers can only create users for their own department.
    Created users will be assigned to manager's department.
    """
    from Services.UserService import UserService
    
    # Get manager's employee record for department
    manager_employee = await get_manager_employee(manager, db)
    
    # Force department to manager's department (ignore provided value)
    user_department = manager_employee.department
    
    user_service = UserService(db)
    
    try:
        user = await user_service.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        # If creating employee, set their department
        if role == "EMPLOYEE":
            from sqlalchemy import select, update
            from Models.Employee import Employee
            
            result = await db.execute(
                select(Employee).where(Employee.email == email)
            )
            employee = result.scalar_one_or_none()
            
            if employee:
                employee.department = user_department
                await db.commit()
        
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "department": user_department if role == "EMPLOYEE" else None,
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
    manager=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user details by ID (department-scoped).
    
    Managers can only view users in their own department.
    """
    from Services.UserService import UserService
    from sqlalchemy import select
    from Models.Employee import Employee
    
    # Get manager's department
    manager_employee = await get_manager_employee(manager, db)
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # If user is an employee, verify department match
    if user.role == UserRole.EMPLOYEE:
        result = await db.execute(
            select(Employee).where(Employee.email == user.email)
        )
        employee = result.scalar_one_or_none()
        
        if not employee or employee.department != manager_employee.department:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only view users in your department"
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
    manager=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for user by email (department-scoped).
    
    Managers can only search for users in their own department.
    """
    from Services.UserService import UserService
    from sqlalchemy import select
    from Models.Employee import Employee
    
    # Get manager's department
    manager_employee = await get_manager_employee(manager, db)
    
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # If user is an employee, verify department match
    if user.role == UserRole.EMPLOYEE:
        result = await db.execute(
            select(Employee).where(Employee.email == user.email)
        )
        employee = result.scalar_one_or_none()
        
        if not employee or employee.department != manager_employee.department:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only search for users in your department"
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
    manager=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user's role (department-scoped).
    
    Managers can only update roles for users in their own department.
    """
    from Services.UserService import UserService
    from sqlalchemy import select
    from Models.Employee import Employee
    
    # Get manager's department
    manager_employee = await get_manager_employee(manager, db)
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # If user is an employee, verify department match
    if user.role == UserRole.EMPLOYEE:
        result = await db.execute(
            select(Employee).where(Employee.email == user.email)
        )
        employee = result.scalar_one_or_none()
        
        if not employee or employee.department != manager_employee.department:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only update roles for users in your department"
            )
    
    try:
        user = await user_service.update_user_role(
            user_id=user_id,
            new_role=new_role,
            admin_user_id=manager.id
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

