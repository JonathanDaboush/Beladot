"""
Scheduling Service

Comprehensive shift scheduling, calendar management, and coverage system.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from Repositories.EmployeeRepository import EmployeeRepository
from Repositories.EmployeeScheduleRepository import EmployeeScheduleRepository
from Repositories.ShiftSwapRepository import ShiftSwapRepository
from Repositories.PaidTimeOffRepository import PaidTimeOffRepository
from Repositories.PaidSickRepository import PaidSickRepository
from Models.EmployeeSchedule import EmployeeSchedule, ShiftType, ScheduleStatus
from Models.ShiftSwap import ShiftSwap, SwapStatus
from Classes.EmployeeSchedule import EmployeeSchedule as ScheduleClass
from typing import List, Dict
from datetime import date, time, datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SchedulingService:
    """Service for managing employee schedules and shifts."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.employee_repo = EmployeeRepository(session)
        self.schedule_repo = EmployeeScheduleRepository(session)
        self.swap_repo = ShiftSwapRepository(session)
        self.pto_repo = PaidTimeOffRepository(session)
        self.sick_repo = PaidSickRepository(session)
    
    async def create_shift(
        self,
        employee_id: int,
        shift_date: date,
        shift_start: time,
        shift_end: time,
        created_by: int,
        shift_type: str = "full_day",
        location: str = None,
        department: str = None,
        notes: str = None
    ) -> EmployeeSchedule:
        """
        Create a new shift for an employee.
        
        Validates shift length, checks for overlaps, and ensures employee availability.
        """
        # Validate employee exists
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        
        # Validate shift using business logic
        schedule_class = ScheduleClass(
            employee_id=employee_id,
            shift_date=shift_date,
            shift_start=shift_start,
            shift_end=shift_end,
            shift_type=shift_type
        )
        
        is_valid, error_msg = schedule_class.is_valid_shift_length()
        if not is_valid:
            raise ValueError(error_msg)
        
        # Check for overlapping shifts
        has_overlap = await self.schedule_repo.check_overlap(
            employee_id,
            shift_date,
            shift_start,
            shift_end
        )
        
        if has_overlap:
            raise ValueError(f"Shift overlaps with existing schedule for employee {employee_id}")
        
        # Check if employee has approved time off
        pto_conflicts = await self.pto_repo.check_conflicts(employee_id, shift_date, shift_date)
        if pto_conflicts:
            raise ValueError(f"Employee has approved time off on {shift_date}")
        
        # Create shift
        shift = EmployeeSchedule(
            employee_id=employee_id,
            created_by=created_by,
            shift_date=shift_date,
            shift_start=shift_start,
            shift_end=shift_end,
            shift_type=ShiftType[shift_type.upper()],
            location=location or employee.work_city,
            department=department or employee.department,
            position=employee.position,
            shift_notes=notes
        )
        
        result = await self.schedule_repo.create(shift)
        logger.info(f"Created shift for employee {employee_id} on {shift_date}")
        
        return result
    
    async def bulk_create_shifts(
        self,
        shifts_data: List[Dict],
        created_by: int
    ) -> Dict:
        """
        Create multiple shifts at once.
        
        Useful for weekly schedule creation.
        """
        results = {
            "success": [],
            "failed": []
        }
        
        for shift_data in shifts_data:
            try:
                shift = await self.create_shift(
                    employee_id=shift_data["employee_id"],
                    shift_date=shift_data["shift_date"],
                    shift_start=shift_data["shift_start"],
                    shift_end=shift_data["shift_end"],
                    created_by=created_by,
                    shift_type=shift_data.get("shift_type", "full_day"),
                    location=shift_data.get("location"),
                    department=shift_data.get("department"),
                    notes=shift_data.get("notes")
                )
                
                results["success"].append({
                    "employee_id": shift.employee_id,
                    "shift_id": shift.id,
                    "shift_date": shift.shift_date.isoformat()
                })
                
            except Exception as e:
                logger.error(f"Failed to create shift: {e}")
                results["failed"].append({
                    "employee_id": shift_data.get("employee_id"),
                    "shift_date": shift_data.get("shift_date"),
                    "error": str(e)
                })
        
        logger.info(f"Bulk created {len(results['success'])} shifts, {len(results['failed'])} failed")
        
        return results
    
    async def get_employee_calendar(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Get employee's calendar view with shifts and time off.
        
        Returns comprehensive view of employee's schedule.
        """
        # Get scheduled shifts
        shifts = await self.schedule_repo.get_by_date_range(
            employee_id,
            start_date,
            end_date
        )
        
        # Get approved time off
        pto_requests = await self.pto_repo.get_approved_by_date_range(start_date, end_date)
        pto_for_employee = [pto for pto in pto_requests if pto.employee_id == employee_id]
        
        sick_requests = await self.sick_repo.get_by_date_range(start_date, end_date)
        sick_for_employee = [sick for sick in sick_requests if sick.employee_id == employee_id]
        
        # Build calendar entries
        calendar = []
        
        for shift in shifts:
            schedule_class = ScheduleClass(
                employee_id=shift.employee_id,
                shift_date=shift.shift_date,
                shift_start=shift.shift_start,
                shift_end=shift.shift_end,
                unpaid_break_minutes=shift.unpaid_break_minutes,
                paid_break_minutes=shift.paid_break_minutes
            )
            
            calendar.append({
                "type": "shift",
                "id": shift.id,
                "date": shift.shift_date.isoformat(),
                "start_time": shift.shift_start.isoformat(),
                "end_time": shift.shift_end.isoformat(),
                "display": schedule_class.get_shift_display(),
                "location": shift.location,
                "department": shift.department,
                "status": shift.status.value,
                "is_confirmed": shift.is_confirmed,
                "needs_coverage": shift.is_coverage_needed
            })
        
        for pto in pto_for_employee:
            calendar.append({
                "type": "pto",
                "id": pto.id,
                "start_date": pto.start_date.isoformat(),
                "end_date": pto.end_date.isoformat(),
                "pto_type": pto.pto_type.value,
                "hours": float(pto.hours_requested),
                "status": pto.status.value
            })
        
        for sick in sick_for_employee:
            calendar.append({
                "type": "sick",
                "id": sick.id,
                "start_date": sick.start_date.isoformat(),
                "end_date": sick.end_date.isoformat(),
                "sick_type": sick.sick_type.value,
                "hours": float(sick.hours_requested),
                "status": sick.status.value
            })
        
        # Sort by date
        calendar.sort(key=lambda x: x.get("date") or x.get("start_date"))
        
        return {
            "employee_id": employee_id,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "entries": calendar,
            "total_shifts": len(shifts),
            "total_pto_days": len(pto_for_employee),
            "total_sick_days": len(sick_for_employee)
        }
    
    async def compare_employee_schedules(
        self,
        employee_ids: List[int] = None,
        start_date: date = None,
        end_date: date = None,
        department: str = None,
        position: str = None,
        location: str = None
    ) -> Dict:
        """
        Compare schedules of multiple employees side-by-side.
        
        Shows overlapping shifts and when employees work together.
        Useful for coordination, coverage planning, and team scheduling.
        
        If employee_ids is None, automatically finds all employees matching criteria.
        If start_date/end_date is None, uses next 30 days.
        """
        # Auto-populate employee IDs if not provided
        if employee_ids is None:
            all_employees = await self.employee_repo.get_all_active()
            
            employee_ids = []
            for employee in all_employees:
                # Department filter
                if department and employee.department != department:
                    continue
                
                # Position filter
                if position and employee.position != position:
                    continue
                
                # Location filter
                if location and employee.work_city != location:
                    continue
                
                employee_ids.append(employee.id)
            
            if not employee_ids:
                return {
                    "message": "No employees found matching the criteria"
                }
        
        # Default to next 30 days if dates not provided
        if start_date is None:
            start_date = date.today()
        if end_date is None:
            end_date = start_date + timedelta(days=30)
        
        all_schedules = {}
        
        for emp_id in employee_ids:
            employee = await self.employee_repo.get_by_id(emp_id)
            if not employee:
                continue
            
            shifts = await self.schedule_repo.get_by_date_range(
                emp_id,
                start_date,
                end_date
            )
            
            all_schedules[emp_id] = {
                "employee": {
                    "id": employee.id,
                    "name": f"{employee.first_name} {employee.last_name}",
                    "department": employee.department,
                    "position": employee.position
                },
                "shifts": []
            }
            
            for shift in shifts:
                schedule_class = ScheduleClass(
                    employee_id=shift.employee_id,
                    shift_date=shift.shift_date,
                    shift_start=shift.shift_start,
                    shift_end=shift.shift_end,
                    unpaid_break_minutes=shift.unpaid_break_minutes
                )
                
                all_schedules[emp_id]["shifts"].append({
                    "id": shift.id,
                    "date": shift.shift_date.isoformat(),
                    "start": shift.shift_start.isoformat(),
                    "end": shift.shift_end.isoformat(),
                    "start_time": shift.shift_start,  # Keep time object for overlap calc
                    "end_time": shift.shift_end,
                    "location": shift.location,
                    "department": shift.department,
                    "status": shift.status.value,
                    "hours": schedule_class.calculate_paid_hours()
                })
        
        # Build day-by-day breakdown with overlaps
        daily_breakdown = {}
        all_dates = set()
        
        for emp_id, data in all_schedules.items():
            for shift in data["shifts"]:
                shift_date = shift["date"]
                all_dates.add(shift_date)
                
                if shift_date not in daily_breakdown:
                    daily_breakdown[shift_date] = []
                
                daily_breakdown[shift_date].append({
                    "employee_id": emp_id,
                    "employee_name": data["employee"]["name"],
                    "position": data["employee"]["position"],
                    "shift_id": shift["id"],
                    "start": shift["start"],
                    "end": shift["end"],
                    "start_time": shift["start_time"],
                    "end_time": shift["end_time"],
                    "hours": shift["hours"],
                    "location": shift["location"],
                    "status": shift["status"]
                })
        
        # Analyze overlaps for each date
        overlap_analysis = {}
        
        for date_str, shifts in daily_breakdown.items():
            # Sort shifts by start time
            shifts_sorted = sorted(shifts, key=lambda x: x["start_time"])
            
            # Find overlapping time periods
            overlaps = []
            
            for i, shift1 in enumerate(shifts_sorted):
                overlapping_with = []
                
                for j, shift2 in enumerate(shifts_sorted):
                    if i == j:
                        continue
                    
                    # Check if shifts overlap
                    start1 = datetime.combine(date.fromisoformat(date_str), shift1["start_time"])
                    end1 = datetime.combine(date.fromisoformat(date_str), shift1["end_time"])
                    start2 = datetime.combine(date.fromisoformat(date_str), shift2["start_time"])
                    end2 = datetime.combine(date.fromisoformat(date_str), shift2["end_time"])
                    
                    # Handle overnight shifts
                    if end1 <= start1:
                        end1 += timedelta(days=1)
                    if end2 <= start2:
                        end2 += timedelta(days=1)
                    
                    # Check overlap
                    if start1 < end2 and start2 < end1:
                        # Calculate overlap duration
                        overlap_start = max(start1, start2)
                        overlap_end = min(end1, end2)
                        overlap_hours = (overlap_end - overlap_start).total_seconds() / 3600
                        
                        overlapping_with.append({
                            "employee_id": shift2["employee_id"],
                            "employee_name": shift2["employee_name"],
                            "overlap_start": overlap_start.time().isoformat(),
                            "overlap_end": overlap_end.time().isoformat(),
                            "overlap_hours": round(overlap_hours, 2)
                        })
                
                if overlapping_with:
                    overlaps.append({
                        "employee_id": shift1["employee_id"],
                        "employee_name": shift1["employee_name"],
                        "shift_start": shift1["start"],
                        "shift_end": shift1["end"],
                        "overlapping_with": overlapping_with
                    })
            
            overlap_analysis[date_str] = {
                "total_employees_scheduled": len(shifts_sorted),
                "shifts": shifts_sorted,
                "overlaps": overlaps,
                "has_overlaps": len(overlaps) > 0
            }
        
        # Calculate summary statistics
        total_overlap_instances = sum(len(day["overlaps"]) for day in overlap_analysis.values())
        days_with_overlaps = sum(1 for day in overlap_analysis.values() if day["has_overlaps"])
        
        return {
            "employees": list(all_schedules.values()),
            "daily_breakdown": overlap_analysis,
            "summary": {
                "total_dates_analyzed": len(all_dates),
                "days_with_multiple_employees": days_with_overlaps,
                "total_overlap_instances": total_overlap_instances,
                "employees_compared": len(all_schedules)
            }
        }
    
    async def request_shift_swap(
        self,
        requesting_employee_id: int,
        target_employee_id: int,
        requesting_shift_id: int,
        target_shift_id: int = None,
        reason: str = None
    ) -> ShiftSwap:
        """
        Request to swap shifts with another employee.
        
        Requires both employee and manager approval.
        """
        # Validate shifts exist
        requesting_shift = await self.schedule_repo.get_by_id(requesting_shift_id)
        if not requesting_shift:
            raise ValueError(f"Requesting shift {requesting_shift_id} not found")
        
        if requesting_shift.employee_id != requesting_employee_id:
            raise ValueError("Requesting employee doesn't own this shift")
        
        if target_shift_id:
            target_shift = await self.schedule_repo.get_by_id(target_shift_id)
            if not target_shift:
                raise ValueError(f"Target shift {target_shift_id} not found")
            
            if target_shift.employee_id != target_employee_id:
                raise ValueError("Target employee doesn't own the target shift")
        
        # Create swap request
        swap = ShiftSwap(
            requesting_employee_id=requesting_employee_id,
            target_employee_id=target_employee_id,
            requesting_shift_id=requesting_shift_id,
            target_shift_id=target_shift_id,
            request_reason=reason
        )
        
        result = await self.swap_repo.create(swap)
        logger.info(f"Shift swap requested between employees {requesting_employee_id} and {target_employee_id}")
        
        return result
    
    async def approve_shift_swap(
        self,
        swap_id: int,
        manager_id: int
    ) -> Dict:
        """
        Approve shift swap and execute the exchange.
        
        Swaps the employee assignments for the two shifts.
        """
        # Get swap request
        swap = await self.swap_repo.get_by_id(swap_id)
        if not swap:
            raise ValueError(f"Swap request {swap_id} not found")
        
        if swap.status != SwapStatus.ACCEPTED_BY_EMPLOYEE:
            raise ValueError("Swap must be accepted by target employee first")
        
        # Approve swap
        await self.swap_repo.approve_by_manager(swap_id, manager_id)
        
        # Execute the swap
        requesting_shift = await self.schedule_repo.get_by_id(swap.requesting_shift_id)
        
        if swap.target_shift_id:
            # Full swap - exchange employees
            target_shift = await self.schedule_repo.get_by_id(swap.target_shift_id)
            
            temp_employee = requesting_shift.employee_id
            requesting_shift.employee_id = target_shift.employee_id
            target_shift.employee_id = temp_employee
            
            await self.schedule_repo.update(requesting_shift)
            await self.schedule_repo.update(target_shift)
            
            logger.info(f"Swapped shifts {swap.requesting_shift_id} and {swap.target_shift_id}")
        else:
            # One-way - just reassign shift
            requesting_shift.employee_id = swap.target_employee_id
            await self.schedule_repo.update(requesting_shift)
            
            logger.info(f"Reassigned shift {swap.requesting_shift_id} to employee {swap.target_employee_id}")
        
        return {
            "swap_id": swap_id,
            "status": "approved",
            "requesting_shift_id": swap.requesting_shift_id,
            "target_shift_id": swap.target_shift_id
        }
    
    async def register_shift_completion(
        self,
        schedule_id: int
    ) -> EmployeeSchedule:
        """
        Register that an employee completed their shift.
        
        Marks shift as completed for payroll processing.
        """
        result = await self.schedule_repo.complete_shift(schedule_id)
        if not result:
            raise ValueError(f"Schedule {schedule_id} not found")
        
        logger.info(f"Shift {schedule_id} marked as completed")
        return result
    
    async def get_coverage_opportunities(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """
        Get available shifts that need coverage that this employee could pick up.
        
        Filters for shifts in employee's department/location without conflicts.
        """
        # Get employee details
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        
        # Get shifts needing coverage
        coverage_needed = await self.schedule_repo.get_coverage_needed(
            start_date,
            end_date,
            location=employee.work_city
        )
        
        # Get employee's current schedule to check conflicts
        employee_shifts = await self.schedule_repo.get_by_date_range(
            employee_id,
            start_date,
            end_date
        )
        
        opportunities = []
        
        for shift in coverage_needed:
            # Check if same department
            if shift.department != employee.department:
                continue
            
            # Check for conflicts
            has_conflict = False
            for emp_shift in employee_shifts:
                if emp_shift.shift_date == shift.shift_date:
                    # Check time overlap
                    schedule_class = ScheduleClass(
                        employee_id=employee_id,
                        shift_date=emp_shift.shift_date,
                        shift_start=emp_shift.shift_start,
                        shift_end=emp_shift.shift_end
                    )
                    
                    if schedule_class.overlaps_with(
                        shift.shift_start,
                        shift.shift_end,
                        shift.shift_date
                    ):
                        has_conflict = True
                        break
            
            if not has_conflict:
                original_employee = await self.employee_repo.get_by_id(shift.employee_id)
                
                opportunities.append({
                    "shift_id": shift.id,
                    "date": shift.shift_date.isoformat(),
                    "start_time": shift.shift_start.isoformat(),
                    "end_time": shift.shift_end.isoformat(),
                    "location": shift.location,
                    "department": shift.department,
                    "original_employee": f"{original_employee.first_name} {original_employee.last_name}",
                    "notes": shift.coverage_notes
                })
        
        return opportunities
