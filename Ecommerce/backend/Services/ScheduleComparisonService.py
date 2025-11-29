"""
Schedule Comparison Service

Advanced schedule comparison and overlap analysis for multiple employees.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from Repositories.EmployeeRepository import EmployeeRepository
from Repositories.EmployeeScheduleRepository import EmployeeScheduleRepository
from Classes.EmployeeSchedule import EmployeeSchedule as ScheduleClass
from typing import List, Dict, Optional
from datetime import date, time, datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ScheduleComparisonService:
    """Service for comparing and analyzing employee schedules."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.employee_repo = EmployeeRepository(session)
        self.schedule_repo = EmployeeScheduleRepository(session)
    
    async def find_employee_ids_by_criteria(
        self,
        department: str = None,
        position: str = None,
        location: str = None,
        exclude_employee_ids: List[int] = None
    ) -> List[int]:
        """
        Find all employee IDs matching the specified criteria.
        
        Returns list of employee IDs to use in comparison methods.
        """
        all_employees = await self.employee_repo.get_all_active()
        
        matching_ids = []
        
        for employee in all_employees:
            # Exclude certain employees
            if exclude_employee_ids and employee.id in exclude_employee_ids:
                continue
            
            # Department filter
            if department and employee.department != department:
                continue
            
            # Position filter
            if position and employee.position != position:
                continue
            
            # Location filter
            if location and employee.work_city != location:
                continue
            
            matching_ids.append(employee.id)
        
        return matching_ids
    
    async def get_overlapping_shifts_with_target(
        self,
        target_employee_id: int,
        comparison_employee_ids: List[int] = None,
        start_date: date = None,
        end_date: date = None,
        department: str = None,
        position: str = None,
        location: str = None,
        time_start: time = None,
        time_end: time = None
    ) -> Dict:
        """
        Show how other employees' schedules overlap with a target employee.
        
        Perfect for seeing who works with a specific employee and when.
        Can filter by department, position/rank, location, and specific time windows.
        
        If comparison_employee_ids is None, automatically finds all employees matching criteria.
        If start_date/end_date is None, uses next 30 days.
        """
        # Get target employee
        target_employee = await self.employee_repo.get_by_id(target_employee_id)
        if not target_employee:
            raise ValueError(f"Target employee {target_employee_id} not found")
        
        # Auto-populate comparison employee IDs if not provided
        if comparison_employee_ids is None:
            comparison_employee_ids = await self.find_employee_ids_by_criteria(
                department=department,
                position=position,
                location=location,
                exclude_employee_ids=[target_employee_id]
            )
            
            if not comparison_employee_ids:
                return {
                    "target_employee": {
                        "id": target_employee.id,
                        "name": f"{target_employee.first_name} {target_employee.last_name}"
                    },
                    "message": "No other employees found matching the criteria"
                }
        
        # Default to next 30 days if dates not provided
        if start_date is None:
            start_date = date.today()
        if end_date is None:
            end_date = start_date + timedelta(days=30)
        
        # Get target employee's shifts
        target_shifts = await self.schedule_repo.get_by_date_range(
            target_employee_id,
            start_date,
            end_date
        )
        
        if not target_shifts:
            return {
                "target_employee": {
                    "id": target_employee.id,
                    "name": f"{target_employee.first_name} {target_employee.last_name}"
                },
                "message": "Target employee has no shifts scheduled in this period"
            }
        
        # Analyze overlaps for each target shift
        target_shifts_analysis = []
        
        for target_shift in target_shifts:
            target_schedule = ScheduleClass(
                employee_id=target_shift.employee_id,
                shift_date=target_shift.shift_date,
                shift_start=target_shift.shift_start,
                shift_end=target_shift.shift_end,
                unpaid_break_minutes=target_shift.unpaid_break_minutes
            )
            
            # Find who else is working during this shift
            overlapping_employees = []
            
            for comp_emp_id in comparison_employee_ids:
                if comp_emp_id == target_employee_id:
                    continue
                
                comp_employee = await self.employee_repo.get_by_id(comp_emp_id)
                if not comp_employee:
                    continue
                
                # Filter by department if specified
                if department and comp_employee.department != department:
                    continue
                
                # Filter by position/rank if specified
                if position and comp_employee.position != position:
                    continue
                
                # Get this employee's shifts on the same date
                comp_shifts = await self.schedule_repo.get_by_employee_and_date(
                    comp_emp_id,
                    target_shift.shift_date
                )
                
                for comp_shift in comp_shifts:
                    # Check for overlap
                    if target_schedule.overlaps_with(
                        comp_shift.shift_start,
                        comp_shift.shift_end,
                        comp_shift.shift_date
                    ):
                        # Calculate overlap period
                        start1 = datetime.combine(target_shift.shift_date, target_shift.shift_start)
                        end1 = datetime.combine(target_shift.shift_date, target_shift.shift_end)
                        start2 = datetime.combine(comp_shift.shift_date, comp_shift.shift_start)
                        end2 = datetime.combine(comp_shift.shift_date, comp_shift.shift_end)
                        
                        # Handle overnight
                        if end1 <= start1:
                            end1 += timedelta(days=1)
                        if end2 <= start2:
                            end2 += timedelta(days=1)
                        
                        overlap_start = max(start1, start2)
                        overlap_end = min(end1, end2)
                        overlap_hours = (overlap_end - overlap_start).total_seconds() / 3600
                        
                        # Filter by time window if specified
                        if time_start and time_end:
                            # Check if overlap falls within requested time window
                            if overlap_start.time() < time_start or overlap_end.time() > time_end:
                                continue
                        
                        overlapping_employees.append({
                            "employee_id": comp_employee.id,
                            "name": f"{comp_employee.first_name} {comp_employee.last_name}",
                            "position": comp_employee.position,
                            "department": comp_employee.department,
                            "their_shift": {
                                "start": comp_shift.shift_start.isoformat(),
                                "end": comp_shift.shift_end.isoformat(),
                                "location": comp_shift.location
                            },
                            "overlap_period": {
                                "start": overlap_start.time().isoformat(),
                                "end": overlap_end.time().isoformat(),
                                "hours": round(overlap_hours, 2)
                            }
                        })
            
            target_shifts_analysis.append({
                "shift_date": target_shift.shift_date.isoformat(),
                "target_shift": {
                    "start": target_shift.shift_start.isoformat(),
                    "end": target_shift.shift_end.isoformat(),
                    "location": target_shift.location,
                    "department": target_shift.department,
                    "hours": target_schedule.calculate_paid_hours()
                },
                "working_with": overlapping_employees,
                "coworkers_count": len(overlapping_employees)
            })
        
        # Summary statistics
        total_coworker_instances = sum(shift["coworkers_count"] for shift in target_shifts_analysis)
        shifts_with_coworkers = sum(1 for shift in target_shifts_analysis if shift["coworkers_count"] > 0)
        shifts_alone = len(target_shifts_analysis) - shifts_with_coworkers
        
        # Find most frequent coworkers
        coworker_frequency = {}
        for shift in target_shifts_analysis:
            for coworker in shift["working_with"]:
                emp_id = coworker["employee_id"]
                if emp_id not in coworker_frequency:
                    coworker_frequency[emp_id] = {
                        "name": coworker["name"],
                        "position": coworker["position"],
                        "count": 0,
                        "total_overlap_hours": 0
                    }
                coworker_frequency[emp_id]["count"] += 1
                coworker_frequency[emp_id]["total_overlap_hours"] += coworker["overlap_period"]["hours"]
        
        # Sort by frequency
        frequent_coworkers = sorted(
            coworker_frequency.values(),
            key=lambda x: x["count"],
            reverse=True
        )
        
        return {
            "target_employee": {
                "id": target_employee.id,
                "name": f"{target_employee.first_name} {target_employee.last_name}",
                "position": target_employee.position,
                "department": target_employee.department
            },
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "shifts": target_shifts_analysis,
            "summary": {
                "total_shifts": len(target_shifts_analysis),
                "shifts_with_coworkers": shifts_with_coworkers,
                "shifts_working_alone": shifts_alone,
                "total_coworker_overlap_instances": total_coworker_instances,
                "unique_coworkers": len(coworker_frequency)
            },
            "frequent_coworkers": frequent_coworkers
        }
    
    async def get_team_schedule_matrix(
        self,
        employee_ids: List[int] = None,
        week_start: date = None,
        department: str = None,
        position: str = None,
        location: str = None
    ) -> Dict:
        """
        Create a matrix view of who works when during a week.
        
        Returns a grid showing all employees and their shifts each day.
        Can filter by department, position/rank, and location.
        
        If employee_ids is None, automatically finds all employees matching criteria.
        If week_start is None, uses current week.
        """
        # Auto-populate employee IDs if not provided
        if employee_ids is None:
            employee_ids = await self.find_employee_ids_by_criteria(
                department=department,
                position=position,
                location=location
            )
            
            if not employee_ids:
                return {
                    "message": "No employees found matching the criteria"
                }
        
        # Default to current week if not provided
        if week_start is None:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        
        week_end = week_start + timedelta(days=6)
        
        # Build matrix structure
        matrix = {}
        employee_details = {}
        
        for emp_id in employee_ids:
            employee = await self.employee_repo.get_by_id(emp_id)
            if not employee:
                continue
            
            # Filter by department if specified
            if department and employee.department != department:
                continue
            
            # Filter by position/rank if specified
            if position and employee.position != position:
                continue
            
            employee_details[emp_id] = {
                "id": employee.id,
                "name": f"{employee.first_name} {employee.last_name}",
                "position": employee.position,
                "department": employee.department
            }
            
            # Get week's shifts
            shifts = await self.schedule_repo.get_weekly_schedule(emp_id, week_start)
            
            # Organize by day
            matrix[emp_id] = {}
            
            current_date = week_start
            for i in range(7):
                date_str = current_date.isoformat()
                matrix[emp_id][date_str] = {
                    "day_name": current_date.strftime("%A"),
                    "shifts": []
                }
                
                # Find shifts for this day
                for shift in shifts:
                    if shift.shift_date == current_date:
                        schedule_class = ScheduleClass(
                            employee_id=shift.employee_id,
                            shift_date=shift.shift_date,
                            shift_start=shift.shift_start,
                            shift_end=shift.shift_end,
                            unpaid_break_minutes=shift.unpaid_break_minutes
                        )
                        
                        matrix[emp_id][date_str]["shifts"].append({
                            "shift_id": shift.id,
                            "start": shift.shift_start.isoformat(),
                            "end": shift.shift_end.isoformat(),
                            "display": schedule_class.get_shift_display(),
                            "hours": schedule_class.calculate_paid_hours(),
                            "status": shift.status.value
                        })
                
                matrix[emp_id][date_str]["total_hours"] = sum(
                    s["hours"] for s in matrix[emp_id][date_str]["shifts"]
                )
                
                current_date += timedelta(days=1)
        
        # Calculate daily staffing levels
        daily_staffing = {}
        current_date = week_start
        
        for i in range(7):
            date_str = current_date.isoformat()
            working_count = sum(
                1 for emp_id in matrix
                if matrix[emp_id][date_str]["shifts"]
            )
            
            daily_staffing[date_str] = {
                "day_name": current_date.strftime("%A"),
                "employees_working": working_count,
                "total_employee_hours": sum(
                    matrix[emp_id][date_str]["total_hours"]
                    for emp_id in matrix
                )
            }
            
            current_date += timedelta(days=1)
        
        return {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "employees": employee_details,
            "schedule_matrix": matrix,
            "daily_staffing": daily_staffing
        }
    
    async def find_common_shifts(
        self,
        employee_ids: List[int] = None,
        start_date: date = None,
        end_date: date = None,
        min_overlap_hours: float = 1.0,
        department: str = None,
        position: str = None,
        location: str = None
    ) -> List[Dict]:
        """
        Find time periods when all specified employees work together.
        
        Useful for scheduling meetings or team activities.
        
        If employee_ids is None, automatically finds all employees matching criteria.
        If start_date/end_date is None, uses next 30 days.
        """
        # Auto-populate employee IDs if not provided
        if employee_ids is None:
            employee_ids = await self.find_employee_ids_by_criteria(
                department=department,
                position=position,
                location=location
            )
            
            if not employee_ids:
                return []
        
        if len(employee_ids) < 2:
            raise ValueError("Need at least 2 employees to find common shifts")
        
        # Default to next 30 days if dates not provided
        if start_date is None:
            start_date = date.today()
        if end_date is None:
            end_date = start_date + timedelta(days=30)
        
        # Get all employees' schedules
        all_shifts = {}
        
        for emp_id in employee_ids:
            shifts = await self.schedule_repo.get_by_date_range(
                emp_id,
                start_date,
                end_date
            )
            all_shifts[emp_id] = shifts
        
        # Find overlapping periods
        common_periods = []
        
        # Get unique dates
        all_dates = set()
        for shifts in all_shifts.values():
            for shift in shifts:
                all_dates.add(shift.shift_date)
        
        # Check each date
        for check_date in sorted(all_dates):
            # Get all employees' shifts on this date
            date_shifts = {}
            
            for emp_id in employee_ids:
                emp_shifts = [s for s in all_shifts[emp_id] if s.shift_date == check_date]
                if not emp_shifts:
                    # If any employee doesn't work this day, skip
                    break
                date_shifts[emp_id] = emp_shifts[0]  # Take first shift
            else:
                # All employees work this day
                # Find the overlapping time period
                starts = [
                    datetime.combine(check_date, date_shifts[emp_id].shift_start)
                    for emp_id in employee_ids
                ]
                ends = [
                    datetime.combine(check_date, date_shifts[emp_id].shift_end)
                    for emp_id in employee_ids
                ]
                
                # Latest start, earliest end
                overlap_start = max(starts)
                overlap_end = min(ends)
                
                if overlap_start < overlap_end:
                    overlap_hours = (overlap_end - overlap_start).total_seconds() / 3600
                    
                    if overlap_hours >= min_overlap_hours:
                        employee_names = []
                        for emp_id in employee_ids:
                            emp = await self.employee_repo.get_by_id(emp_id)
                            employee_names.append(f"{emp.first_name} {emp.last_name}")
                        
                        common_periods.append({
                            "date": check_date.isoformat(),
                            "overlap_start": overlap_start.time().isoformat(),
                            "overlap_end": overlap_end.time().isoformat(),
                            "overlap_hours": round(overlap_hours, 2),
                            "employees": employee_names,
                            "employee_count": len(employee_ids)
                        })
        
        return common_periods
