"""
Scheduling Routes
Handles employee scheduling operations

TODO: These routes need proper User-Employee linking. Currently using basic auth.
Employees should have linked User accounts to access their schedules.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import Optional, List, Dict

from database import get_db
from schemas import MessageResponse
from Services.SchedulingService import SchedulingService
from Utilities.auth import get_current_user, get_current_admin_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/schedule", tags=["Scheduling"])


@router.get("/my-schedule", dependencies=[Depends(rate_limiter_moderate)])
async def get_my_schedule(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get schedule for current employee
    
    TODO: Implement User-to-Employee linking to fetch correct employee_id
    """
    scheduling_service = SchedulingService(db)
    
    # TODO: Get employee_id from user-employee mapping
    # For now, using user.id as placeholder - this needs proper implementation
    schedule = await scheduling_service.get_employee_schedule(current_user.id)
    
    return {"schedule": schedule}
@router.get("/all", dependencies=[Depends(rate_limiter_moderate)])
async def get_all_schedules(
    start_date: date,
    end_date: date,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get schedules for all employees (Admin only)"""
    scheduling_service = SchedulingService(db)
    
    schedules = await scheduling_service.get_schedules_by_date_range(start_date, end_date)
    
    return {"schedules": schedules}


@router.post("/shifts", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def create_shift(
    employee_id: int,
    shift_date: date,
    shift_start: str,
    shift_end: str,
    location: str,
    department: str,
    position: str,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new shift (Admin only)"""
    scheduling_service = SchedulingService(db)
    
    await scheduling_service.create_shift(
        employee_id=employee_id,
        shift_date=shift_date,
        shift_start=shift_start,
        shift_end=shift_end,
        location=location,
        department=department,
        position=position
    )
    
    return {"message": "Shift created successfully"}


@router.post("/shifts/bulk", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def bulk_create_shifts(
    shifts: List[Dict],
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create multiple shifts at once (Admin only)"""
    scheduling_service = SchedulingService(db)
    
    await scheduling_service.bulk_create_shifts(shifts)
    
    return {"message": f"{len(shifts)} shifts created successfully"}


@router.post("/shifts/recurring", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def create_recurring_shifts(
    employee_id: int,
    days_of_week: List[str],
    shift_start: str,
    shift_end: str,
    location: str,
    department: str,
    position: str,
    weeks: int,
    start_date: date,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create recurring shifts (Admin only)"""
    scheduling_service = SchedulingService(db)
    
    await scheduling_service.create_recurring_shifts(
        employee_id=employee_id,
        days_of_week=days_of_week,
        shift_start=shift_start,
        shift_end=shift_end,
        location=location,
        department=department,
        position=position,
        weeks=weeks,
        start_date=start_date
    )
    
    return {"message": f"Recurring shifts created for {weeks} weeks"}


@router.delete("/shifts/{shift_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def cancel_shift(
    shift_id: int,
    reason: Optional[str] = None,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a shift (Admin only)"""
    scheduling_service = SchedulingService(db)
    
    await scheduling_service.cancel_shift(
        shift_id=shift_id,
        cancelled_by=current_admin.id,
        reason=reason
    )
    
    return {"message": "Shift cancelled successfully"}


@router.put("/shifts/{shift_id}/time", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_shift_time(
    shift_id: int,
    new_start: Optional[str] = None,
    new_end: Optional[str] = None,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update shift time (Admin only)"""
    scheduling_service = SchedulingService(db)
    
    await scheduling_service.update_shift_time(
        shift_id=shift_id,
        new_start=new_start,
        new_end=new_end,
        updated_by=current_admin.id
    )
    
    return {"message": "Shift time updated successfully"}


@router.get("/coverage", dependencies=[Depends(rate_limiter_moderate)])
async def check_coverage(
    target_date: date,
    department: str,
    position: Optional[str] = None,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Check staffing coverage for a date (Admin only)"""
    scheduling_service = SchedulingService(db)
    
    coverage = await scheduling_service.check_coverage(
        target_date=target_date,
        department=department,
        position=position
    )
    
    return {"coverage": coverage}


@router.get("/available-employees", dependencies=[Depends(rate_limiter_moderate)])
async def get_available_employees(
    target_date: date,
    shift_start: str,
    shift_end: str,
    department: Optional[str] = None,
    position: Optional[str] = None,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Find available employees for a shift (Admin only)"""
    scheduling_service = SchedulingService(db)
    
    available = await scheduling_service.get_available_employees(
        target_date=target_date,
        shift_start=shift_start,
        shift_end=shift_end,
        department=department,
        position=position
    )
    
    return {"available_employees": available}


@router.post("/swap-request", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def request_shift_swap(
    my_shift_id: int,
    target_employee_id: int,
    target_shift_id: Optional[int] = None,
    reason: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Request to swap shifts with another employee"""
    scheduling_service = SchedulingService(db)
    
    await scheduling_service.request_shift_swap(
        requesting_employee_id=current_user.id,
        my_shift_id=my_shift_id,
        target_employee_id=target_employee_id,
        target_shift_id=target_shift_id,
        reason=reason
    )
    
    return {"message": "Shift swap request submitted"}


@router.post("/swap-request/{swap_id}/approve", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def approve_shift_swap(
    swap_id: int,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve shift swap request (Admin only)"""
    scheduling_service = SchedulingService(db)
    
    await scheduling_service.approve_shift_swap(
        swap_id=swap_id,
        approved_by=current_admin.id
    )
    
    return {"message": "Shift swap approved"}

