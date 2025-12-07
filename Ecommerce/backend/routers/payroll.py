"""
Payroll Routes
Handles employee payroll operations (employee self-service)

TODO: These routes need proper User-Employee linking. Currently using basic auth.
Employees should have linked User accounts to view their payroll.
Note: Finance role has separate payroll management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from database import get_db
from schemas import MessageResponse
from Services.PayrollService import PayrollService
from Utilities.auth import get_current_user, get_current_admin_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/payroll", tags=["Payroll"])


@router.get("/my-payroll", dependencies=[Depends(rate_limiter_moderate)])
async def get_my_payroll(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payroll information for current employee
    
    TODO: Implement User-to-Employee linking to fetch correct employee_id
    """
    payroll_service = PayrollService(db)
    
    # TODO: Get employee_id from user-employee mapping
    payroll = await payroll_service.get_employee_payroll(current_user.id)  # Placeholder
    
    return {"payroll": payroll}


@router.post("/calculate", dependencies=[Depends(rate_limiter_moderate)])
async def calculate_payroll(
    start_date: date,
    end_date: date,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Calculate payroll for all employees (Admin only)"""
    payroll_service = PayrollService(db)
    
    results = await payroll_service.calculate_payroll(start_date, end_date)
    
    return {"payroll_results": results}


@router.post("/calculate-paycheck", dependencies=[Depends(rate_limiter_moderate)])
async def calculate_single_paycheck(
    employee_id: int,
    start_date: date,
    end_date: date,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Calculate paycheck for single employee (Admin only)"""
    payroll_service = PayrollService(db)
    
    paycheck = await payroll_service.calculate_paycheck(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {"paycheck": paycheck}


@router.get("/pay-summary", dependencies=[Depends(rate_limiter_moderate)])
async def get_pay_summary(
    employee_id: int,
    start_date: date,
    end_date: date,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get employee pay summary (Admin only)"""
    payroll_service = PayrollService(db)
    
    summary = await payroll_service.get_employee_pay_summary(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {"pay_summary": summary}


@router.get("/my-pay-summary", dependencies=[Depends(rate_limiter_moderate)])
async def get_my_pay_summary(
    start_date: date,
    end_date: date,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get own pay summary"""
    payroll_service = PayrollService(db)
    
    summary = await payroll_service.get_employee_pay_summary(
        employee_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {"pay_summary": summary}

