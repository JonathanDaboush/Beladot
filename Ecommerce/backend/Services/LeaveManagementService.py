"""
Leave Management Service

Handles PTO and sick leave requests, approvals, and balance tracking.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from Repositories.EmployeeRepository import EmployeeRepository
from Repositories.PaidTimeOffRepository import PaidTimeOffRepository
from Repositories.PaidSickRepository import PaidSickRepository
from Models.PaidTimeOff import PaidTimeOff, PTOType
from Models.PaidSick import PaidSick, SickLeaveType
from Classes.PaidTimeOff import PaidTimeOff as PTOClass
from Classes.PaidSick import PaidSick as SickClass
from typing import List, Dict
from datetime import date
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class LeaveManagementService:
    """Service for managing employee leave (PTO and sick leave)."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.employee_repo = EmployeeRepository(session)
        self.pto_repo = PaidTimeOffRepository(session)
        self.sick_repo = PaidSickRepository(session)
    
    async def request_pto(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        hours_requested: float,
        pto_type: str = "vacation",
        notes: str = None
    ) -> PaidTimeOff:
        """
        Submit PTO request.
        
        Validates dates, hours, and balance before creating request.
        """
        # Get current PTO balance
        from Classes.Employee import Employee as EmployeeClass
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        
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
        balance_data = await self.pto_repo.calculate_pto_balance(employee_id, accrual_rate)
        
        # Validate using business logic
        pto_class = PTOClass(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            hours_requested=Decimal(str(hours_requested)),
            pto_type=pto_type,
            request_notes=notes,
            balance_before=Decimal(str(balance_data["hours_remaining"]))
        )
        
        # Validate dates
        is_valid, error_msg = pto_class.validate_dates()
        if not is_valid:
            raise ValueError(error_msg)
        
        # Validate hours
        is_valid, error_msg = pto_class.validate_hours()
        if not is_valid:
            raise ValueError(error_msg)
        
        # Check sufficient balance
        if not pto_class.is_sufficient_balance():
            raise ValueError(f"Insufficient PTO balance. Available: {balance_data['hours_remaining']}h")
        
        # Check for conflicts
        conflicts = await self.pto_repo.check_conflicts(employee_id, start_date, end_date)
        if conflicts:
            raise ValueError(f"PTO request conflicts with existing approved leave")
        
        # Create PTO request
        pto = PaidTimeOff(
            employee_id=employee_id,
            pto_type=PTOType[pto_type.upper()],
            start_date=start_date,
            end_date=end_date,
            hours_requested=Decimal(str(hours_requested)),
            request_notes=notes,
            balance_before=Decimal(str(balance_data["hours_remaining"])),
            balance_after=pto_class.calculate_balance_after()
        )
        
        result = await self.pto_repo.create(pto)
        logger.info(f"PTO request created for employee {employee_id}: {hours_requested}h from {start_date} to {end_date}")
        
        return result
    
    async def request_sick_leave(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        hours_requested: float,
        sick_type: str = "illness",
        reason: str = None
    ) -> PaidSick:
        """
        Submit sick leave request.
        
        Can be submitted retroactively within 7 days.
        """
        # Get current sick leave balance
        from Classes.Employee import Employee as EmployeeClass
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        
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
        balance_data = await self.sick_repo.calculate_sick_balance(employee_id, accrual_rate)
        
        # Validate using business logic
        sick_class = SickClass(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            hours_requested=Decimal(str(hours_requested)),
            sick_type=sick_type,
            reason_notes=reason,
            balance_before=Decimal(str(balance_data["hours_remaining"]))
        )
        
        # Validate dates
        is_valid, error_msg = sick_class.validate_dates()
        if not is_valid:
            raise ValueError(error_msg)
        
        # Validate hours
        is_valid, error_msg = sick_class.validate_hours()
        if not is_valid:
            raise ValueError(error_msg)
        
        # Check if doctor's note required
        requires_note = sick_class.requires_doctors_note()
        
        # Create sick leave request
        sick = PaidSick(
            employee_id=employee_id,
            sick_type=SickLeaveType[sick_type.upper()],
            start_date=start_date,
            end_date=end_date,
            hours_requested=Decimal(str(hours_requested)),
            reason_notes=reason,
            balance_before=Decimal(str(balance_data["hours_remaining"])),
            balance_after=sick_class.calculate_balance_after(),
            requires_doctors_note=requires_note
        )
        
        result = await self.sick_repo.create(sick)
        logger.info(f"Sick leave request created for employee {employee_id}: {hours_requested}h from {start_date} to {end_date}")
        
        return result
    
    async def approve_pto(self, pto_id: int, reviewed_by: int) -> PaidTimeOff:
        """Approve PTO request."""
        result = await self.pto_repo.approve_request(pto_id, reviewed_by)
        if not result:
            raise ValueError(f"PTO request {pto_id} not found")
        
        logger.info(f"PTO request {pto_id} approved by employee {reviewed_by}")
        return result
    
    async def deny_pto(
        self,
        pto_id: int,
        reviewed_by: int,
        reason: str
    ) -> PaidTimeOff:
        """Deny PTO request."""
        result = await self.pto_repo.deny_request(pto_id, reviewed_by, reason)
        if not result:
            raise ValueError(f"PTO request {pto_id} not found")
        
        logger.info(f"PTO request {pto_id} denied by employee {reviewed_by}")
        return result
    
    async def approve_sick_leave(self, sick_id: int, reviewed_by: int) -> PaidSick:
        """Approve sick leave request."""
        result = await self.sick_repo.approve_request(sick_id, reviewed_by)
        if not result:
            raise ValueError(f"Sick leave request {sick_id} not found")
        
        logger.info(f"Sick leave request {sick_id} approved by employee {reviewed_by}")
        return result
    
    async def get_leave_calendar(
        self,
        start_date: date,
        end_date: date,
        department: str = None
    ) -> Dict:
        """
        Get calendar view of all approved leave.
        
        Useful for scheduling and coverage planning.
        """
        pto_requests = await self.pto_repo.get_approved_by_date_range(start_date, end_date)
        sick_requests = await self.sick_repo.get_by_date_range(start_date, end_date)
        
        calendar = []
        
        for pto in pto_requests:
            employee = await self.employee_repo.get_by_id(pto.employee_id)
            
            # Filter by department if specified
            if department and employee.department != department:
                continue
            
            calendar.append({
                "type": "pto",
                "employee": {
                    "id": employee.id,
                    "name": f"{employee.first_name} {employee.last_name}",
                    "department": employee.department
                },
                "start_date": pto.start_date.isoformat(),
                "end_date": pto.end_date.isoformat(),
                "hours": float(pto.hours_requested),
                "pto_type": pto.pto_type.value
            })
        
        for sick in sick_requests:
            employee = await self.employee_repo.get_by_id(sick.employee_id)
            
            if department and employee.department != department:
                continue
            
            calendar.append({
                "type": "sick",
                "employee": {
                    "id": employee.id,
                    "name": f"{employee.first_name} {employee.last_name}",
                    "department": employee.department
                },
                "start_date": sick.start_date.isoformat(),
                "end_date": sick.end_date.isoformat(),
                "hours": float(sick.hours_requested),
                "sick_type": sick.sick_type.value
            })
        
        # Sort by start date
        calendar.sort(key=lambda x: x["start_date"])
        
        return {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "department": department,
            "total_requests": len(calendar),
            "requests": calendar
        }
