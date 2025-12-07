"""
Scheduling Extended Router
Adds calendar view, shift completion, and coverage opportunities
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import Optional

from database import get_db
from schemas import MessageResponse
from Services.SchedulingService import SchedulingService
from Utilities.auth import get_current_user, get_current_admin_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/schedule", tags=["Scheduling Extended"])


@router.get("/calendar", dependencies=[Depends(rate_limiter_moderate)])
async def get_employee_calendar(
    start_date: date,
    end_date: date,
    employee_id: Optional[int] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get calendar view for employee (own or specified if admin)"""
    scheduling_service = SchedulingService(db)
    
    # If no employee_id, use current user
    target_employee_id = employee_id if employee_id else current_user.id
    
    calendar = await scheduling_service.get_employee_calendar(
        employee_id=target_employee_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {"calendar": calendar}


@router.post("/shift/{shift_id}/complete", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def mark_shift_complete(
    shift_id: int,
    notes: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark shift as completed (employee self-service)"""
    scheduling_service = SchedulingService(db)
    
    await scheduling_service.register_shift_completion(
        shift_id=shift_id,
        completed_by=current_user.id,
        notes=notes
    )
    
    return {"message": "Shift marked as completed"}


@router.get("/open-shifts", dependencies=[Depends(rate_limiter_moderate)])
async def get_open_shifts(
    target_date: date,
    department: Optional[str] = None,
    position: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get open shifts needing coverage (shift marketplace)"""
    scheduling_service = SchedulingService(db)
    
    opportunities = await scheduling_service.get_coverage_opportunities(
        target_date=target_date,
        department=department,
        position=position
    )
    
    return {"open_shifts": opportunities}


@router.get("/compare", dependencies=[Depends(rate_limiter_moderate)])
async def compare_schedules(
    employee_id_1: int,
    employee_id_2: int,
    start_date: date,
    end_date: date,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Compare schedules between two employees (admin only)"""
    scheduling_service = SchedulingService(db)
    
    comparison = await scheduling_service.compare_employee_schedules(
        employee_id_1=employee_id_1,
        employee_id_2=employee_id_2,
        start_date=start_date,
        end_date=end_date
    )
    
    return {"comparison": comparison}
