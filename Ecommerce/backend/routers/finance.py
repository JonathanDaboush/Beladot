"""
Finance Routes
Handles financial operations:
- Employee payroll processing
- Payment management
- Financial data and reporting
- Payment information updates
- Salary adjustments
- Tax and deduction management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from database import get_db
from schemas import MessageResponse
from Services.PayrollService import PayrollService
from Services.PaymentService import PaymentService
from Services.AnalyticsService import AnalyticsService
from Utilities.auth import get_current_finance
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/finance", tags=["Finance"])


# ============================================================================
# PAYROLL MANAGEMENT
# ============================================================================

@router.post("/payroll/calculate", dependencies=[Depends(rate_limiter_moderate)])
async def calculate_payroll(
    start_date: date,
    end_date: date,
    current_finance=Depends(get_current_finance),
    db: AsyncSession = Depends(get_db)
):
    """Calculate payroll for all employees (Finance only)"""
    payroll_service = PayrollService(db)
    
    results = await payroll_service.calculate_payroll(start_date, end_date)
    
    return {"payroll_results": results}


@router.post("/payroll/process", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def process_payroll(
    employee_id: int,
    amount: Decimal,
    pay_period_start: date,
    pay_period_end: date,
    current_finance=Depends(get_current_finance),
    db: AsyncSession = Depends(get_db)
):
    """Process payroll payment for an employee (Finance only)"""
    payroll_service = PayrollService(db)
    
    await payroll_service.process_payroll_payment(
        employee_id=employee_id,
        amount=amount,
        pay_period_start=pay_period_start,
        pay_period_end=pay_period_end,
        processed_by=current_finance.id
    )
    
    return {"message": f"Payroll processed for employee {employee_id}"}


@router.get("/payroll/employee/{employee_id}", dependencies=[Depends(rate_limiter_moderate)])
async def get_employee_payroll(
    employee_id: int,
    current_finance=Depends(get_current_finance),
    db: AsyncSession = Depends(get_db)
):
    """Get payroll history for an employee (Finance only)"""
    payroll_service = PayrollService(db)
    
    payroll = await payroll_service.get_employee_payroll(employee_id)
    
    return {"payroll": payroll}


@router.put("/payroll/employee/{employee_id}/salary", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_employee_salary(
    employee_id: int,
    new_salary: Decimal,
    effective_date: date,
    reason: str,
    current_finance=Depends(get_current_finance),
    db: AsyncSession = Depends(get_db)
):
    """Update employee salary (Finance only)"""
    payroll_service = PayrollService(db)
    
    await payroll_service.update_salary(
        employee_id=employee_id,
        new_salary=new_salary,
        effective_date=effective_date,
        reason=reason,
        updated_by=current_finance.id
    )
    
    return {"message": f"Salary updated for employee {employee_id}"}


# ============================================================================
# PAYMENT MANAGEMENT
# ============================================================================

@router.get("/payments", dependencies=[Depends(rate_limiter_moderate)])
async def get_all_payments(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_finance=Depends(get_current_finance),
    db: AsyncSession = Depends(get_db)
):
    """Get all payments with optional date filters (Finance only)"""
    payment_service = PaymentService(db)
    
    payments = await payment_service.get_payments_by_date_range(start_date, end_date)
    
    return {"payments": payments}


@router.post("/payments/{payment_id}/refund", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def process_refund(
    payment_id: int,
    amount: Decimal,
    reason: str,
    current_finance=Depends(get_current_finance),
    db: AsyncSession = Depends(get_db)
):
    """Process refund for a payment (Finance only)"""
    payment_service = PaymentService(db)
    
    await payment_service.process_refund(
        payment_id=payment_id,
        amount=amount,
        reason=reason,
        processed_by=current_finance.id
    )
    
    return {"message": f"Refund of {amount} processed for payment {payment_id}"}


@router.put("/payments/{payment_id}/adjust", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def adjust_payment(
    payment_id: int,
    adjustment_amount: Decimal,
    reason: str,
    current_finance=Depends(get_current_finance),
    db: AsyncSession = Depends(get_db)
):
    """Adjust payment amount (Finance only)"""
    payment_service = PaymentService(db)
    
    await payment_service.adjust_payment(
        payment_id=payment_id,
        adjustment_amount=adjustment_amount,
        reason=reason,
        adjusted_by=current_finance.id
    )
    
    return {"message": f"Payment {payment_id} adjusted by {adjustment_amount}"}


# ============================================================================
# FINANCIAL REPORTING
# ============================================================================

@router.get("/reports/revenue", dependencies=[Depends(rate_limiter_moderate)])
async def get_revenue_report(
    start_date: date,
    end_date: date,
    current_finance=Depends(get_current_finance),
    db: AsyncSession = Depends(get_db)
):
    """Get revenue report for date range (Finance only)"""
    analytics_service = AnalyticsService(db)
    
    revenue = await analytics_service.get_revenue_report(start_date, end_date)
    
    return {"revenue_report": revenue}


@router.get("/reports/expenses", dependencies=[Depends(rate_limiter_moderate)])
async def get_expense_report(
    start_date: date,
    end_date: date,
    current_finance=Depends(get_current_finance),
    db: AsyncSession = Depends(get_db)
):
    """Get expense report including payroll (Finance only)"""
    analytics_service = AnalyticsService(db)
    
    expenses = await analytics_service.get_expense_report(start_date, end_date)
    
    return {"expense_report": expenses}


@router.get("/reports/profit-loss", dependencies=[Depends(rate_limiter_moderate)])
async def get_profit_loss_report(
    start_date: date,
    end_date: date,
    current_finance=Depends(get_current_finance),
    db: AsyncSession = Depends(get_db)
):
    """Get profit & loss statement (Finance only)"""
    analytics_service = AnalyticsService(db)
    
    pl_report = await analytics_service.get_profit_loss_report(start_date, end_date)
    
    return {"profit_loss_report": pl_report}


# ============================================================================
# EMPLOYEE FINANCIAL INFO
# ============================================================================

@router.get("/employees/{employee_id}/financial", dependencies=[Depends(rate_limiter_moderate)])
async def get_employee_financial_info(
    employee_id: int,
    current_finance=Depends(get_current_finance),
    db: AsyncSession = Depends(get_db)
):
    """Get employee financial information (Finance only)"""
    payroll_service = PayrollService(db)
    
    financial_info = await payroll_service.get_employee_financial_info(employee_id)
    
    return {"financial_info": financial_info}


@router.put("/employees/{employee_id}/financial", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_employee_financial_info(
    employee_id: int,
    data: dict,
    current_finance=Depends(get_current_finance),
    db: AsyncSession = Depends(get_db)
):
    """Update employee financial information (salary, deductions, etc.) (Finance only)"""
    payroll_service = PayrollService(db)
    
    await payroll_service.update_employee_financial_info(
        employee_id=employee_id,
        financial_data=data,
        updated_by=current_finance.id
    )
    
    return {"message": f"Financial information updated for employee {employee_id}"}


@router.post("/employees/{employee_id}/tax-info", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_tax_information(
    employee_id: int,
    tax_data: dict,
    current_finance=Depends(get_current_finance),
    db: AsyncSession = Depends(get_db)
):
    """Update employee tax information (Finance only)"""
    payroll_service = PayrollService(db)
    
    await payroll_service.update_tax_information(
        employee_id=employee_id,
        tax_data=tax_data,
        updated_by=current_finance.id
    )
    
    return {"message": f"Tax information updated for employee {employee_id}"}


@router.get("/paycheck/{employee_id}", dependencies=[Depends(rate_limiter_moderate)])
async def get_employee_paycheck(
    employee_id: int,
    current_finance=Depends(get_current_finance),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paycheck details for any employee (Finance only).
    
    Shows:
    - Gross pay
    - Deductions
    - Net pay
    - Hours breakdown (regular, overtime, etc.)
    """
    from sqlalchemy import select
    from Models.Employee import Employee
    from datetime import timedelta
    
    # Verify employee exists
    result = await db.execute(
        select(Employee).where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    payroll_service = PayrollService(db)
    
    try:
        # Calculate paycheck for specified employee
        paycheck = await payroll_service.calculate_paycheck(
            employee_id=employee_id,
            pay_period_start=date.today() - timedelta(days=14),  # Last 2 weeks
            pay_period_end=date.today()
        )
        
        return {
            "employee_id": employee.id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "employee_number": employee.employee_number,
            "department": employee.department,
            "pay_period": {
                "start": paycheck.get("pay_period_start"),
                "end": paycheck.get("pay_period_end")
            },
            "hours": {
                "regular": float(paycheck.get("regular_hours", 0)),
                "overtime": float(paycheck.get("overtime_hours", 0)),
                "double_time": float(paycheck.get("double_time_hours", 0)),
                "holiday": float(paycheck.get("holiday_hours", 0)),
                "total": float(paycheck.get("total_hours", 0))
            },
            "earnings": {
                "gross_pay": float(paycheck.get("gross_pay", 0)),
                "regular_pay": float(paycheck.get("regular_pay", 0)),
                "overtime_pay": float(paycheck.get("overtime_pay", 0)),
                "holiday_pay": float(paycheck.get("holiday_pay", 0))
            },
            "deductions": paycheck.get("deductions", {}),
            "net_pay": float(paycheck.get("net_pay", 0))
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

