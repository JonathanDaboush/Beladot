"""
Leave Management Routes
Handles PTO, sick leave, and time-off requests

TODO: These routes need proper User-Employee linking. Currently using basic auth.
Employees should have linked User accounts to request and view leave.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import Optional

from database import get_db
from schemas import MessageResponse
from Services.LeaveManagementService import LeaveManagementService
from Utilities.auth import get_current_user, get_current_admin_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/leave", tags=["Leave Management"])


@router.post("/pto/request", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def request_pto(
    start_date: date,
    end_date: date,
    reason: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Request paid time off
    
    TODO: Implement User-to-Employee linking to fetch correct employee_id
    """
    leave_service = LeaveManagementService(db)
    
    # TODO: Get employee_id from user-employee mapping
    await leave_service.request_pto(
        employee_id=current_user.id,  # Placeholder - needs proper mapping
        start_date=start_date,
        end_date=end_date,
        reason=reason
    )
    
    return {"message": "PTO request submitted"}


@router.get("/my-requests", dependencies=[Depends(rate_limiter_moderate)])
async def get_my_leave_requests(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get leave requests for current employee
    
    TODO: Implement User-to-Employee linking to fetch correct employee_id
    """
    leave_service = LeaveManagementService(db)
    
    # TODO: Get employee_id from user-employee mapping
    requests = await leave_service.get_employee_leave_requests(current_user.id)  # Placeholder
    
    return {"leave_requests": requests}


@router.post("/approve/{request_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def approve_leave(
    request_id: int,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve leave request (Admin only)"""
    leave_service = LeaveManagementService(db)
    
    await leave_service.approve_leave_request(request_id, current_admin.id)
    
    return {"message": "Leave request approved"}


@router.post("/sick-leave/request", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def request_sick_leave(
    start_date: date,
    end_date: date,
    reason: str,
    documentation: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Request sick leave"""
    leave_service = LeaveManagementService(db)
    
    await leave_service.request_sick_leave(
        employee_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        documentation=documentation
    )
    
    return {"message": "Sick leave request submitted"}


@router.post("/pto/{request_id}/deny", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def deny_pto(
    request_id: int,
    reason: str,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Deny PTO request (Admin only)"""
    leave_service = LeaveManagementService(db)
    
    await leave_service.deny_pto(
        pto_id=request_id,
        reviewed_by=current_admin.id,
        reason=reason
    )
    
    return {"message": "PTO request denied"}


@router.post("/sick-leave/{request_id}/approve", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def approve_sick_leave(
    request_id: int,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve sick leave request (Admin only)"""
    leave_service = LeaveManagementService(db)
    
    await leave_service.approve_sick_leave(
        sick_id=request_id,
        reviewed_by=current_admin.id
    )
    
    return {"message": "Sick leave approved"}


@router.get("/calendar", dependencies=[Depends(rate_limiter_moderate)])
async def get_leave_calendar(
    start_date: date,
    end_date: date,
    department: Optional[str] = None,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get leave calendar for team/department (Admin only)"""
    leave_service = LeaveManagementService(db)
    
    calendar = await leave_service.get_leave_calendar(
        start_date=start_date,
        end_date=end_date,
        department=department
    )
    
    return {"calendar": calendar}


@router.get("/balance/pto", dependencies=[Depends(rate_limiter_moderate)])
async def get_pto_balance(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current PTO balance"""
    leave_service = LeaveManagementService(db)
    
    balance = await leave_service.get_pto_balance(employee_id=current_user.id)
    
    return {"pto_balance": balance}


@router.get("/balance/sick", dependencies=[Depends(rate_limiter_moderate)])
async def get_sick_balance(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current sick leave balance"""
    leave_service = LeaveManagementService(db)
    
    balance = await leave_service.get_sick_balance(employee_id=current_user.id)
    
    return {"sick_balance": balance}


@router.delete("/pto/{request_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def cancel_pto_request(
    request_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel PTO request (before approval)"""
    leave_service = LeaveManagementService(db)
    
    await leave_service.cancel_pto_request(
        pto_id=request_id,
        employee_id=current_user.id
    )
    
    return {"message": "PTO request cancelled"}


@router.get("/history", dependencies=[Depends(rate_limiter_moderate)])
async def get_leave_history(
    employee_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get leave history"""
    leave_service = LeaveManagementService(db)
    
    # If employee_id not specified, use current user
    target_employee_id = employee_id if employee_id else current_user.id
    
    history = await leave_service.get_leave_history(
        employee_id=target_employee_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {"leave_history": history}

