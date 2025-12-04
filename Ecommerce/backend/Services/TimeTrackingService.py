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
            raise ValueError(f"Employee {employee_id} not clocked in")
        
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
        
        # Calculate total hours from clock times
        total_from_clock = hours_class.calculate_hours_from_clock_times()
        
        # Split into regular and overtime
        hour_split = hours_class.split_regular_and_overtime()
        hours.regular_hours = hour_split["regular_hours"]
        hours.overtime_hours = hour_split["overtime_hours"]
        hours.total_hours = total_from_clock
        
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
    
    async def reject_hours(
        self,
        hours_id: int,
        rejected_by: int,
        reason: str = None
    ) -> HoursWorked:
        """Reject hours worked entry."""
        hours = await self.hours_repo.get_by_id(hours_id)
        if not hours:
            raise ValueError(f"Hours entry {hours_id} not found")
        
        if hours.is_approved:
            raise ValueError(f"Cannot reject already approved hours")
        
        # Mark as not approved and add rejection reason to notes
        hours.is_approved = False
        hours.approved_by = rejected_by
        hours.approved_at = datetime.now()
        if reason:
            hours.notes = f"REJECTED: {reason}" + (f" | Previous notes: {hours.notes}" if hours.notes else "")
        
        result = await self.hours_repo.update(hours)
        logger.info(f"Hours {hours_id} rejected by employee {rejected_by}")
        return result
    
    async def calculate_hours_worked(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> Dict:
        """Calculate total hours worked for a date range."""
        result = await self.hours_repo.calculate_total_hours(employee_id, start_date, end_date)
        return result
    
    async def calculate_hours(self, hours_id: int) -> HoursWorked:
        """Calculate hours for a specific hours record from clock times."""
        hours = await self.hours_repo.get_by_id(hours_id)
        if not hours:
            raise ValueError(f"Hours entry {hours_id} not found")
        
        if not hours.clock_in or not hours.clock_out:
            raise ValueError("Cannot calculate hours without clock in and clock out times")
        
        # Calculate using business logic
        hours_class = HoursWorkedClass(
            employee_id=hours.employee_id,
            work_date=hours.work_date,
            clock_in=hours.clock_in,
            clock_out=hours.clock_out
        )
        
        # Calculate total hours from clock times
        total_from_clock = hours_class.calculate_hours_from_clock_times()
        
        # Split into regular and overtime
        hour_split = hours_class.split_regular_and_overtime()
        hours.regular_hours = hour_split["regular_hours"]
        hours.overtime_hours = hour_split["overtime_hours"]
        hours.total_hours = total_from_clock
        
        result = await self.hours_repo.update(hours)
        logger.info(f"Calculated hours for entry {hours_id}: {result.total_hours}h")
        return result
    
    async def edit_hours(
        self,
        hours_id: int,
        clock_in: datetime = None,
        clock_out: datetime = None,
        regular_hours: float = None,
        overtime_hours: float = None,
        notes: str = None
    ) -> HoursWorked:
        """Edit hours entry (only allowed before approval)."""
        hours = await self.hours_repo.get_by_id(hours_id)
        if not hours:
            raise ValueError(f"Hours entry {hours_id} not found")
        
        if hours.is_approved:
            raise ValueError("Cannot edit approved hours")
        
        # Update fields
        if clock_in is not None:
            hours.clock_in = clock_in
        if clock_out is not None:
            hours.clock_out = clock_out
        if regular_hours is not None:
            hours.regular_hours = Decimal(str(regular_hours))
        if overtime_hours is not None:
            hours.overtime_hours = Decimal(str(overtime_hours))
        if notes is not None:
            hours.notes = notes
        
        # Recalculate total if clock times changed
        if clock_in or clock_out:
            if hours.clock_in and hours.clock_out:
                hours_class = HoursWorkedClass(
                    employee_id=hours.employee_id,
                    work_date=hours.work_date,
                    clock_in=hours.clock_in,
                    clock_out=hours.clock_out
                )
                total_from_clock = hours_class.calculate_hours_from_clock_times()
                hour_split = hours_class.split_regular_and_overtime()
                hours.regular_hours = hour_split["regular_hours"]
                hours.overtime_hours = hour_split["overtime_hours"]
                hours.total_hours = total_from_clock
        elif regular_hours is not None or overtime_hours is not None:
            hours.total_hours = hours.regular_hours + hours.overtime_hours
        
        result = await self.hours_repo.update(hours)
        logger.info(f"Hours {hours_id} edited")
        return result
    
    async def add_break_time(
        self,
        hours_id: int,
        break_minutes: int
    ) -> HoursWorked:
        """Add break time to deduct from total hours."""
        hours = await self.hours_repo.get_by_id(hours_id)
        if not hours:
            raise ValueError(f"Hours entry {hours_id} not found")
        
        # Store the break time in minutes
        hours.unpaid_break_minutes = (hours.unpaid_break_minutes or 0) + break_minutes
        
        # Deduct break time from total hours
        break_hours = Decimal(str(break_minutes)) / Decimal("60")
        hours.total_hours = max(Decimal("0"), hours.total_hours - break_hours)
        
        # Adjust regular hours if needed
        if hours.regular_hours > hours.total_hours:
            hours.regular_hours = hours.total_hours
            hours.overtime_hours = Decimal("0")
        
        result = await self.hours_repo.update(hours)
        logger.info(f"Added {break_minutes} min break to hours {hours_id}")
        return result
    
    async def batch_approve_hours(
        self,
        hours_ids: List[int],
        approved_by: int
    ) -> List[Dict]:
        """Approve multiple hours entries at once."""
        results = []
        
        for hours_id in hours_ids:
            try:
                hours = await self.approve_hours(hours_id, approved_by)
                results.append({
                    "hours_id": hours_id,
                    "employee_id": hours.employee_id,
                    "total_hours": float(hours.total_hours),
                    "status": "approved"
                })
            except Exception as e:
                logger.error(f"Failed to approve hours {hours_id}: {e}")
                results.append({
                    "hours_id": hours_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        logger.info(f"Batch approved {len(results)} hours entries")
        return results
    
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
            "total_hours": total_hours,
            "total_regular_hours": total_regular,
            "total_overtime_hours": total_overtime,
            "total_entries": len(entries_data),
            "approved_entries": approved_count,
            "pending_approval": len(entries_data) - approved_count,
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
