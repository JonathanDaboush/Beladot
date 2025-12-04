"""
Payroll Service

Handles all payroll-related business logic including:
- Time tracking and approval
- Paycheck calculations
- Tax withholding
- PTO/sick leave accruals
- Payroll batch processing
"""

from sqlalchemy.ext.asyncio import AsyncSession
from Repositories.EmployeeRepository import EmployeeRepository
from Repositories.EmployeeFinancialRepository import EmployeeFinancialRepository
from Repositories.HoursWorkedRepository import HoursWorkedRepository
from Repositories.PaidTimeOffRepository import PaidTimeOffRepository
from Repositories.PaidSickRepository import PaidSickRepository
from Classes.EmployeeFinancial import EmployeeFinancial as EmployeeFinancialClass
from typing import List, Dict
from datetime import date, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PayrollService:
    """Main payroll service for managing employee compensation."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.employee_repo = EmployeeRepository(session)
        self.financial_repo = EmployeeFinancialRepository(session)
        self.hours_repo = HoursWorkedRepository(session)
        self.pto_repo = PaidTimeOffRepository(session)
        self.sick_repo = PaidSickRepository(session)
    
    async def calculate_paycheck(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Calculate paycheck for an employee for a pay period.
        
        Returns breakdown of gross pay, deductions, and net pay.
        """
        # Get employee financial info
        financial = await self.financial_repo.get_by_employee_id(employee_id)
        if not financial:
            raise ValueError(f"No financial information found for employee {employee_id}")
        
        # Get hours worked for pay period
        hours_data = await self.hours_repo.calculate_total_hours(
            employee_id,
            start_date,
            end_date
        )
        
        # Validate hours are not negative
        if hours_data["regular_hours"] < 0 or hours_data["overtime_hours"] < 0:
            raise ValueError("Hours cannot be negative")
        if not financial:
            raise ValueError(f"No financial information found for employee {employee_id}")
        
        # Get hours worked for pay period
        hours_data = await self.hours_repo.calculate_total_hours(
            employee_id,
            start_date,
            end_date
        )
        
        # Create business logic instance
        financial_class = EmployeeFinancialClass(
            employee_id=financial.employee_id,
            pay_rate=financial.pay_rate,
            is_salary=financial.is_salary,
            overtime_eligible=financial.overtime_eligible,
            payment_frequency=financial.payment_frequency.value,
            payment_method=financial.payment_method.value
        )
        
        # Calculate gross pay
        gross_pay = financial_class.calculate_gross_pay(
            regular_hours=Decimal(str(hours_data["regular_hours"])),
            overtime_hours=Decimal(str(hours_data["overtime_hours"])),
            overtime_multiplier=financial.overtime_rate_multiplier
        )
        
        # Calculate overtime pay separately for reporting
        overtime_pay = (
            Decimal(str(hours_data["overtime_hours"])) * 
            financial.pay_rate * 
            financial.overtime_rate_multiplier
        ) if hours_data["overtime_hours"] > 0 else Decimal("0")
        
        # Get YTD deductions (simplified - would query payroll history in production)
        ytd_cpp = Decimal("0")  # Would calculate from previous paychecks
        ytd_ei = Decimal("0")    # Would calculate from previous paychecks
        
        # Calculate deductions (handle None values)
        other_deductions = (
            (financial.health_insurance_deduction or Decimal("0")) +
            (financial.retirement_contribution or Decimal("0")) +
            (financial.other_deductions or Decimal("0"))
        )
        
        net_pay_breakdown = financial_class.calculate_net_pay(
            gross_pay,
            ytd_cpp,
            ytd_ei,
            other_deductions
        )
        
        # Add pay period info
        net_pay_breakdown.update({
            "employee_id": employee_id,
            "pay_period_start": start_date.isoformat(),
            "pay_period_end": end_date.isoformat(),
            "hours_breakdown": hours_data,
            "pay_rate": float(financial.pay_rate),
            "is_salary": financial.is_salary,
            "overtime_pay": overtime_pay
        })
        
        logger.info(f"Calculated paycheck for employee {employee_id}: ${net_pay_breakdown['net_pay']}")
        
        return net_pay_breakdown
    
    async def process_payroll_batch(
        self,
        pay_period_start: date,
        pay_period_end: date,
        employee_ids: List[int] = None
    ) -> Dict:
        """
        Process payroll for multiple employees.
        
        If employee_ids not provided, processes all active employees.
        Returns summary of processed paychecks.
        """
        if employee_ids is None:
            # Get all active employees
            employees = await self.employee_repo.get_all_active()
            employee_ids = [emp.id for emp in employees]
        
        results = {
            "success": [],
            "failed": [],
            "total_gross": Decimal("0"),
            "total_net": Decimal("0")
        }
        
        for emp_id in employee_ids:
            try:
                paycheck = await self.calculate_paycheck(
                    emp_id,
                    pay_period_start,
                    pay_period_end
                )
                
                gross = Decimal(str(paycheck["gross_pay"]))
                net = Decimal(str(paycheck["net_pay"]))
                
                results["success"].append({
                    "employee_id": emp_id,
                    "gross_pay": float(gross),
                    "net_pay": float(net)
                })
                
                results["total_gross"] += gross
                results["total_net"] += net
                
            except Exception as e:
                logger.error(f"Failed to process payroll for employee {emp_id}: {e}")
                results["failed"].append({
                    "employee_id": emp_id,
                    "error": str(e)
                })
        
        # Convert totals to float for JSON serialization
        results["total_gross"] = float(results["total_gross"])
        results["total_net"] = float(results["total_net"])
        
        logger.info(f"Processed payroll batch: {len(results['success'])} success, {len(results['failed'])} failed")
        
        return results
    
    async def accrue_pto(self, employee_id: int) -> Dict:
        """
        Accrue PTO for an employee (called each pay period).
        
        Returns updated PTO balance.
        """
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        
        # Calculate accrual rate based on tenure
        from Classes.Employee import Employee as EmployeeClass
        emp_class = EmployeeClass(
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email,
            employee_number=employee.employee_number,
            position=employee.position,
            department=employee.department,
            hire_date=employee.hire_date
        )
        
        accrual_rate = Decimal(str(emp_class.calculate_pto_accrual_rate()))
        
        # Get current balance
        balance_data = await self.pto_repo.calculate_pto_balance(
            employee_id,
            accrual_rate
        )
        
        logger.info(f"Accrued {accrual_rate} PTO hours for employee {employee_id}")
        
        return balance_data
    
    async def accrue_sick_leave(self, employee_id: int) -> Dict:
        """
        Accrue sick leave for an employee (called each pay period).
        
        Returns updated sick leave balance.
        """
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        
        # Calculate sick leave accrual rate
        from Classes.Employee import Employee as EmployeeClass
        emp_class = EmployeeClass(
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email,
            employee_number=employee.employee_number,
            position=employee.position,
            department=employee.department,
            hire_date=employee.hire_date
        )
        
        accrual_rate = Decimal(str(emp_class.calculate_sick_accrual_rate()))
        
        # Get current balance
        balance_data = await self.sick_repo.calculate_sick_balance(
            employee_id,
            accrual_rate
        )
        
        logger.info(f"Accrued {accrual_rate} sick hours for employee {employee_id}")
        
        return balance_data
    
    async def get_employee_pay_summary(
        self,
        employee_id: int,
        year: int = None
    ) -> Dict:
        """
        Get comprehensive pay summary for an employee.
        
        Includes YTD earnings, hours, PTO, sick leave, etc.
        """
        if year is None:
            year = date.today().year
        
        start_of_year = date(year, 1, 1)
        end_of_year = date(year, 12, 31)
        
        # Get employee and financial info
        employee = await self.employee_repo.get_by_id(employee_id)
        financial = await self.financial_repo.get_by_employee_id(employee_id)
        
        if not employee or not financial:
            raise ValueError(f"Employee or financial data not found for {employee_id}")
        
        # Get YTD hours
        hours_data = await self.hours_repo.calculate_total_hours(
            employee_id,
            start_of_year,
            end_of_year
        )
        
        # Get PTO balance
        from Classes.Employee import Employee as EmployeeClass
        emp_class = EmployeeClass(
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email,
            employee_number=employee.employee_number,
            position=employee.position,
            department=employee.department,
            hire_date=employee.hire_date
        )
        
        pto_accrual = Decimal(str(emp_class.calculate_pto_accrual_rate()))
        sick_accrual = Decimal(str(emp_class.calculate_sick_accrual_rate()))
        
        pto_balance = await self.pto_repo.calculate_pto_balance(employee_id, pto_accrual, year)
        sick_balance = await self.sick_repo.calculate_sick_balance(employee_id, sick_accrual, year)
        
        return {
            "employee": {
                "id": employee.id,
                "name": f"{employee.first_name} {employee.last_name}",
                "employee_number": employee.employee_number,
                "position": employee.position,
                "department": employee.department
            },
            "compensation": {
                "pay_rate": float(financial.pay_rate),
                "is_salary": financial.is_salary,
                "payment_frequency": financial.payment_frequency.value
            },
            "ytd_hours": hours_data,
            "pto": pto_balance,
            "sick_leave": sick_balance,
            "year": year
        }
    
    # Alias for test compatibility
    async def process_batch_payroll(
        self,
        employee_ids: List[int],
        pay_period_start: date,
        pay_period_end: date
    ):
        """Alias for process_payroll_batch with different parameter order."""
        result = await self.process_payroll_batch(
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            employee_ids=employee_ids
        )
        # Return just the success list for backward compatibility
        return result["success"]

