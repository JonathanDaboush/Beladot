"""
Time Tracking Service

Handles time tracking, hour approval, and timesheet management.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from Repositories.EmployeeRepository import EmployeeRepository
from Repositories.HoursWorkedRepository import HoursWorkedRepository
from Models.HoursWorked import HoursWorked
from Classes.HoursWorked import HoursWorked as HoursWorkedClass
from typing import List, Dict
from datetime import date, datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class TimeTrackingService:
    """Service for managing employee time tracking."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.employee_repo = EmployeeRepository(session)
        self.hours_repo = HoursWorkedRepository(session)
    
    async def clock_in(self, employee_id: int) -> HoursWorked:
        """
        Clock in an employee.
        Creates a new hours_worked entry with clock_in time.
        """
        # Check if employee already clocked in today
        today = date.today()
        existing = await self.hours_repo.get_by_employee_and_date(employee_id, today)
        
        if existing and existing.clock_in and not existing.clock_out:
            raise ValueError(f"Employee {employee_id} is already clocked in")
        
        # Create new hours entry
        hours = HoursWorked(
            employee_id=employee_id,
            work_date=today,
            clock_in=datetime.now(),
            regular_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            double_time_hours=Decimal("0"),
            holiday_hours=Decimal("0"),
            total_hours=Decimal("0")
        )
        
        result = await self.hours_repo.create(hours)
        logger.info(f"Employee {employee_id} clocked in at {result.clock_in}")
        
        return result
    
    async def clock_out(self, employee_id: int) -> HoursWorked:
        """
        Clock out an employee.
        Calculates hours worked and splits into regular/overtime.
        """
        today = date.today()
        hours = await self.hours_repo.get_by_employee_and_date(employee_id, today)
        
        if not hours:
            raise ValueError(f"No clock-in found for employee {employee_id} today")
        
        if hours.clock_out:
            raise ValueError(f"Employee {employee_id} already clocked out")
        
        # Set clock out time
        hours.clock_out = datetime.now()
        
        # Calculate hours using business logic
        hours_class = HoursWorkedClass(
            employee_id=employee_id,
            work_date=today,
            clock_in=hours.clock_in,
            clock_out=hours.clock_out
        )
        
        # Split into regular and overtime
        hour_split = hours_class.split_regular_and_overtime()
        hours.regular_hours = hour_split["regular_hours"]
        hours.overtime_hours = hour_split["overtime_hours"]
        hours.total_hours = hours_class.calculate_total_hours()
        
        result = await self.hours_repo.update(hours)
        logger.info(f"Employee {employee_id} clocked out at {result.clock_out}. Total: {result.total_hours}h")
        
        return result
    
    async def submit_manual_hours(
        self,
        employee_id: int,
        work_date: date,
        regular_hours: float,
        overtime_hours: float = 0.0,
        notes: str = None
    ) -> HoursWorked:
        """
        Submit manual hours entry (for salaried employees or corrections).
        """
        # Check for existing entry
        existing = await self.hours_repo.get_by_employee_and_date(employee_id, work_date)
        if existing:
            raise ValueError(f"Hours already submitted for {work_date}")
        
        # Validate hours
        hours_class = HoursWorkedClass(
            employee_id=employee_id,
            work_date=work_date,
            regular_hours=Decimal(str(regular_hours)),
            overtime_hours=Decimal(str(overtime_hours))
        )
        
        is_valid, error_msg = hours_class.validate_hours()
        if not is_valid:
            raise ValueError(error_msg)
        
        # Create hours entry
        hours = HoursWorked(
            employee_id=employee_id,
            work_date=work_date,
            regular_hours=Decimal(str(regular_hours)),
            overtime_hours=Decimal(str(overtime_hours)),
            double_time_hours=Decimal("0"),
            holiday_hours=Decimal("0"),
            total_hours=hours_class.calculate_total_hours(),
            notes=notes
        )
        
        result = await self.hours_repo.create(hours)
        logger.info(f"Manual hours submitted for employee {employee_id}: {result.total_hours}h on {work_date}")
        
        return result
    
    async def approve_hours(
        self,
        hours_id: int,
        approved_by: int
    ) -> HoursWorked:
        """Approve hours worked entry."""
        result = await self.hours_repo.approve_hours(hours_id, approved_by)
        if not result:
            raise ValueError(f"Hours entry {hours_id} not found")
        
        logger.info(f"Hours {hours_id} approved by employee {approved_by}")
        return result
    
    async def get_timesheet(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Get employee timesheet for a date range.
        
        Returns summary with hours breakdown and approval status.
        """
        hours_entries = await self.hours_repo.get_by_date_range(
            employee_id,
            start_date,
            end_date
        )
        
        # Calculate totals
        total_hours = Decimal("0")
        total_regular = Decimal("0")
        total_overtime = Decimal("0")
        approved_count = 0
        
        entries_data = []
        for entry in hours_entries:
            total_hours += entry.total_hours
            total_regular += entry.regular_hours
            total_overtime += entry.overtime_hours
            
            if entry.is_approved:
                approved_count += 1
            
            entries_data.append({
                "id": entry.id,
                "work_date": entry.work_date.isoformat(),
                "clock_in": entry.clock_in.isoformat() if entry.clock_in else None,
                "clock_out": entry.clock_out.isoformat() if entry.clock_out else None,
                "regular_hours": float(entry.regular_hours),
                "overtime_hours": float(entry.overtime_hours),
                "total_hours": float(entry.total_hours),
                "is_approved": entry.is_approved,
                "notes": entry.notes
            })
        
        return {
            "employee_id": employee_id,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "entries": entries_data,
            "summary": {
                "total_hours": float(total_hours),
                "regular_hours": float(total_regular),
                "overtime_hours": float(total_overtime),
                "total_entries": len(entries_data),
                "approved_entries": approved_count,
                "pending_approval": len(entries_data) - approved_count
            }
        }
    
    async def get_pending_approvals(self, manager_id: int) -> List[Dict]:
        """Get all hours entries pending approval for a manager's team."""
        pending = await self.hours_repo.get_pending_approval(manager_id)
        
        results = []
        for entry in pending:
            employee = await self.employee_repo.get_by_id(entry.employee_id)
            
            results.append({
                "hours_id": entry.id,
                "employee": {
                    "id": employee.id,
                    "name": f"{employee.first_name} {employee.last_name}",
                    "employee_number": employee.employee_number
                },
                "work_date": entry.work_date.isoformat(),
                "total_hours": float(entry.total_hours),
                "regular_hours": float(entry.regular_hours),
                "overtime_hours": float(entry.overtime_hours),
                "notes": entry.notes
            })
        
        return results
