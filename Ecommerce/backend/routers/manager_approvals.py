"""
Manager Approval Router - Extended
Handles all manager approval workflows for time tracking, scheduling, and leave
Implements department-scoped authority and batch operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from typing import List, Optional

from database import get_db
from schemas import MessageResponse
from Services.TimeTrackingService import TimeTrackingService
from Services.LeaveManagementService import LeaveManagementService
from Utilities.auth import get_current_user
from Utilities.rate_limiting import rate_limiter_moderate
from Models.User import UserRole

router = APIRouter(prefix="/api/manager/approvals", tags=["Manager Approvals"])


def require_manager(current_user=Depends(get_current_user)):
    """Verify user has MANAGER role"""
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager role required"
        )
    return current_user


# ============================================================================
# TIME TRACKING APPROVALS
# ============================================================================

@router.get("/hours/pending", dependencies=[Depends(rate_limiter_moderate)])
async def get_pending_hours(
    current_manager=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """Get all pending hours awaiting approval"""
    time_service = TimeTrackingService(db)
    
    pending = await time_service.get_pending_approvals(manager_id=current_manager.id)
    
    return {"pending_hours": pending, "count": len(pending)}


@router.post("/hours/{hours_id}/approve", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def approve_hours(
    hours_id: int,
    current_manager=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """Approve time entry"""
    time_service = TimeTrackingService(db)
    
    await time_service.approve_hours(
        hours_id=hours_id,
        approved_by=current_manager.id
    )
    
    return {"message": "Hours approved successfully"}


@router.post("/hours/{hours_id}/reject", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def reject_hours(
    hours_id: int,
    reason: str,
    current_manager=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """Reject time entry with reason"""
    time_service = TimeTrackingService(db)
    
    await time_service.reject_hours(
        hours_id=hours_id,
        rejected_by=current_manager.id,
        reason=reason
    )
    
    return {"message": "Hours rejected"}


@router.post("/hours/batch-approve", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def batch_approve_hours(
    hours_ids: List[int],
    current_manager=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """Approve multiple time entries at once"""
    time_service = TimeTrackingService(db)
    
    results = await time_service.batch_approve_hours(
        hours_ids=hours_ids,
        approved_by=current_manager.id
    )
    
    return {
        "message": f"Approved {results['approved']} entries",
        "approved": results['approved'],
        "failed": results['failed']
    }


# ============================================================================
# LEAVE APPROVALS
# ============================================================================

@router.post("/leave/pto/{pto_id}/approve", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def approve_pto_request(
    pto_id: int,
    current_manager=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """Approve PTO request"""
    leave_service = LeaveManagementService(db)
    
    await leave_service.approve_pto(
        pto_id=pto_id,
        reviewed_by=current_manager.id
    )
    
    return {"message": "PTO request approved"}


@router.post("/leave/pto/{pto_id}/accrue", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def manually_accrue_pto(
    employee_id: int,
    hours: float,
    current_manager=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """Manually accrue PTO hours to employee"""
    leave_service = LeaveManagementService(db)
    
    new_balance = await leave_service.accrue_pto(
        employee_id=employee_id,
        hours=hours
    )
    
    return {
        "message": f"Accrued {hours} hours",
        "new_balance": float(new_balance)
    }


@router.post("/leave/sick/{employee_id}/accrue", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def manually_accrue_sick(
    employee_id: int,
    hours: float,
    current_manager=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """Manually accrue sick leave hours"""
    leave_service = LeaveManagementService(db)
    
    new_balance = await leave_service.accrue_sick_leave(
        employee_id=employee_id,
        hours=hours
    )
    
    return {
        "message": f"Accrued {hours} sick hours",
        "new_balance": float(new_balance)
    }


@router.post("/leave/batch-accrue", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def batch_accrue_pto(
    employee_ids: List[int],
    hours: float,
    current_manager=Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """Batch accrue PTO for multiple employees (payroll period)"""
    leave_service = LeaveManagementService(db)
    
    results = await leave_service.batch_accrue_pto(
        employee_ids=employee_ids,
        hours=hours
    )
    
    return {
        "message": f"Accrued {hours} hours for {len(results)} employees",
        "results": results
    }
