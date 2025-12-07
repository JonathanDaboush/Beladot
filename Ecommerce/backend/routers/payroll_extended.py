"""
Payroll Extended Router
Adds batch processing and automated accruals
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import List

from database import get_db
from schemas import MessageResponse
from Services.PayrollService import PayrollService
from Utilities.auth import get_current_admin_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/payroll", tags=["Payroll Extended"])


@router.post("/process-batch", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def process_payroll_batch(
    start_date: date,
    end_date: date,
    employee_ids: List[int],
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Process payroll batch for specified employees
    Admin only - runs complete payroll cycle
    """
    payroll_service = PayrollService(db)
    
    results = await payroll_service.process_payroll_batch(
        start_date=start_date,
        end_date=end_date,
        employee_ids=employee_ids,
        processed_by=current_admin.id
    )
    
    return {
        "message": f"Processed payroll for {len(results)} employees",
        "processed": len(results),
        "total_amount": sum(r.get("net_pay", 0) for r in results)
    }


@router.post("/accrue-pto/{employee_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def auto_accrue_pto(
    employee_id: int,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Auto-accrue PTO based on hours worked
    Admin only - runs accrual calculation
    """
    payroll_service = PayrollService(db)
    
    result = await payroll_service.accrue_pto(employee_id=employee_id)
    
    return {
        "message": "PTO accrued successfully",
        "hours_accrued": result.get("hours_accrued"),
        "new_balance": result.get("new_balance")
    }


@router.post("/accrue-sick/{employee_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def auto_accrue_sick(
    employee_id: int,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Auto-accrue sick leave based on hours worked
    Admin only - runs accrual calculation
    """
    payroll_service = PayrollService(db)
    
    result = await payroll_service.accrue_sick_leave(employee_id=employee_id)
    
    return {
        "message": "Sick leave accrued successfully",
        "hours_accrued": result.get("hours_accrued"),
        "new_balance": result.get("new_balance")
    }


@router.post("/process-full-batch", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def process_full_payroll(
    start_date: date,
    end_date: date,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Process complete payroll batch with banking integration
    Admin only - full payroll run
    """
    payroll_service = PayrollService(db)
    
    results = await payroll_service.process_batch_payroll(
        start_date=start_date,
        end_date=end_date,
        processed_by=current_admin.id
    )
    
    return {
        "message": "Full payroll processed",
        "employees_paid": results.get("employees_paid"),
        "total_amount": results.get("total_amount"),
        "batch_id": results.get("batch_id")
    }
