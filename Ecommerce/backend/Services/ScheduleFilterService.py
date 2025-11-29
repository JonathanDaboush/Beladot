"""
Schedule Filter Service

Advanced filtering for employee schedules by department, position, time frame, and rank.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from Repositories.EmployeeRepository import EmployeeRepository
from Repositories.EmployeeScheduleRepository import EmployeeScheduleRepository
from Classes.EmployeeSchedule import EmployeeSchedule as ScheduleClass
from typing import List, Dict, Optional
from datetime import date, time, datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ScheduleFilterService:
    """Service for filtering and querying schedules with advanced criteria."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.employee_repo = EmployeeRepository(session)
        self.schedule_repo = EmployeeScheduleRepository(session)
    
    async def get_employees_by_criteria(
        self,
        start_date: date,
        end_date: date,
        department: str = None,
        position: str = None,
        location: str = None,
        time_start: time = None,
        time_end: time = None,
        min_hours: float = None,
        max_hours: float = None,
        sort_by: str = "name"  # name, position, hours, shift_count
    ) -> Dict:
        """
        Get employees working within specified criteria.
        
        Filters by department, position/rank, location, time windows, and hours.
        Returns sorted results based on selected criteria.
        """
        # Get all active employees
        all_employees = await self.employee_repo.get_all_active()
        
        # Filter employees by department, position, location
        filtered_employees = []
        
        for employee in all_employees:
            # Department filter
            if department and employee.department != department:
                continue
            
            # Position/rank filter
            if position and employee.position != position:
                continue
            
            # Location filter
            if location and employee.work_city != location:
                continue
            
            filtered_employees.append(employee)
        
        # Now get schedules for filtered employees
        employee_schedules = []
        
        for employee in filtered_employees:
            shifts = await self.schedule_repo.get_by_date_range(
                employee.id,
                start_date,
                end_date
            )
            
            # Apply time and hours filters
            filtered_shifts = []
            total_hours = 0.0
            
            for shift in shifts:
                # Time window filter
                if time_start and time_end:
                    # Check if shift overlaps with time window
                    if shift.shift_start >= time_end or shift.shift_end <= time_start:
                        continue
                
                schedule_class = ScheduleClass(
                    employee_id=shift.employee_id,
                    shift_date=shift.shift_date,
                    shift_start=shift.shift_start,
                    shift_end=shift.shift_end,
                    unpaid_break_minutes=shift.unpaid_break_minutes
                )
                
                shift_hours = schedule_class.calculate_paid_hours()
                total_hours += shift_hours
                
                filtered_shifts.append({
                    "id": shift.id,
                    "date": shift.shift_date.isoformat(),
                    "start": shift.shift_start.isoformat(),
                    "end": shift.shift_end.isoformat(),
                    "hours": shift_hours,
                    "location": shift.location,
                    "status": shift.status.value
                })
            
            # Hours filter
            if min_hours is not None and total_hours < min_hours:
                continue
            
            if max_hours is not None and total_hours > max_hours:
                continue
            
            # Only include if they have shifts
            if filtered_shifts:
                employee_schedules.append({
                    "employee": {
                        "id": employee.id,
                        "name": f"{employee.first_name} {employee.last_name}",
                        "employee_number": employee.employee_number,
                        "department": employee.department,
                        "position": employee.position,
                        "location": employee.work_city
                    },
                    "shifts": filtered_shifts,
                    "total_hours": round(total_hours, 2),
                    "shift_count": len(filtered_shifts),
                    "average_hours_per_shift": round(total_hours / len(filtered_shifts), 2) if filtered_shifts else 0
                })
        
        # Sort results
        if sort_by == "name":
            employee_schedules.sort(key=lambda x: x["employee"]["name"])
        elif sort_by == "position":
            employee_schedules.sort(key=lambda x: x["employee"]["position"])
        elif sort_by == "hours":
            employee_schedules.sort(key=lambda x: x["total_hours"], reverse=True)
        elif sort_by == "shift_count":
            employee_schedules.sort(key=lambda x: x["shift_count"], reverse=True)
        
        return {
            "filters": {
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "department": department,
                "position": position,
                "location": location,
                "time_window": {
                    "start": time_start.isoformat() if time_start else None,
                    "end": time_end.isoformat() if time_end else None
                },
                "hours_range": {
                    "min": min_hours,
                    "max": max_hours
                },
                "sort_by": sort_by
            },
            "results": employee_schedules,
            "summary": {
                "total_employees": len(employee_schedules),
                "total_hours": sum(e["total_hours"] for e in employee_schedules),
                "total_shifts": sum(e["shift_count"] for e in employee_schedules)
            }
        }
    
    async def get_department_schedule(
        self,
        department: str,
        start_date: date,
        end_date: date,
        group_by_position: bool = False
    ) -> Dict:
        """
        Get complete schedule for a department.
        
        Optionally group by position/rank to see hierarchy.
        """
        # Get employees in department
        employees = await self.employee_repo.get_by_department(department)
        
        if not employees:
            return {
                "department": department,
                "message": "No employees found in this department"
            }
        
        department_schedule = []
        position_groups = {}
        
        for employee in employees:
            shifts = await self.schedule_repo.get_by_date_range(
                employee.id,
                start_date,
                end_date
            )
            
            total_hours = 0.0
            shift_list = []
            
            for shift in shifts:
                schedule_class = ScheduleClass(
                    employee_id=shift.employee_id,
                    shift_date=shift.shift_date,
                    shift_start=shift.shift_start,
                    shift_end=shift.shift_end,
                    unpaid_break_minutes=shift.unpaid_break_minutes
                )
                
                shift_hours = schedule_class.calculate_paid_hours()
                total_hours += shift_hours
                
                shift_list.append({
                    "date": shift.shift_date.isoformat(),
                    "start": shift.shift_start.isoformat(),
                    "end": shift.shift_end.isoformat(),
                    "hours": shift_hours,
                    "location": shift.location
                })
            
            employee_data = {
                "employee": {
                    "id": employee.id,
                    "name": f"{employee.first_name} {employee.last_name}",
                    "position": employee.position,
                    "employee_number": employee.employee_number
                },
                "shifts": shift_list,
                "total_hours": round(total_hours, 2),
                "shift_count": len(shift_list)
            }
            
            department_schedule.append(employee_data)
            
            # Group by position
            if group_by_position:
                position = employee.position
                if position not in position_groups:
                    position_groups[position] = {
                        "position": position,
                        "employees": [],
                        "total_hours": 0.0,
                        "employee_count": 0
                    }
                
                position_groups[position]["employees"].append(employee_data)
                position_groups[position]["total_hours"] += total_hours
                position_groups[position]["employee_count"] += 1
        
        result = {
            "department": department,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "employees": department_schedule,
            "summary": {
                "total_employees": len(department_schedule),
                "total_hours": sum(e["total_hours"] for e in department_schedule),
                "total_shifts": sum(e["shift_count"] for e in department_schedule)
            }
        }
        
        if group_by_position:
            result["by_position"] = list(position_groups.values())
        
        return result
    
    async def get_position_hierarchy_schedule(
        self,
        start_date: date,
        end_date: date,
        department: str = None,
        position_hierarchy: List[str] = None
    ) -> Dict:
        """
        Get schedules organized by position hierarchy/rank.
        
        Shows organizational structure with schedules.
        Example hierarchy: ["Manager", "Supervisor", "Lead", "Associate"]
        """
        if not position_hierarchy:
            # Default hierarchy
            position_hierarchy = [
                "Director",
                "Manager",
                "Assistant Manager",
                "Supervisor",
                "Team Lead",
                "Senior",
                "Associate",
                "Junior"
            ]
        
        # Get all active employees
        all_employees = await self.employee_repo.get_all_active()
        
        # Filter by department if specified
        if department:
            all_employees = [e for e in all_employees if e.department == department]
        
        # Group by position
        hierarchy_schedule = {}
        
        for position in position_hierarchy:
            hierarchy_schedule[position] = {
                "position": position,
                "rank": position_hierarchy.index(position) + 1,
                "employees": [],
                "total_hours": 0.0,
                "employee_count": 0
            }
        
        # Add "Other" category for positions not in hierarchy
        hierarchy_schedule["Other"] = {
            "position": "Other",
            "rank": len(position_hierarchy) + 1,
            "employees": [],
            "total_hours": 0.0,
            "employee_count": 0
        }
        
        for employee in all_employees:
            shifts = await self.schedule_repo.get_by_date_range(
                employee.id,
                start_date,
                end_date
            )
            
            if not shifts:
                continue
            
            total_hours = 0.0
            shift_list = []
            
            for shift in shifts:
                schedule_class = ScheduleClass(
                    employee_id=shift.employee_id,
                    shift_date=shift.shift_date,
                    shift_start=shift.shift_start,
                    shift_end=shift.shift_end,
                    unpaid_break_minutes=shift.unpaid_break_minutes
                )
                
                shift_hours = schedule_class.calculate_paid_hours()
                total_hours += shift_hours
                
                shift_list.append({
                    "date": shift.shift_date.isoformat(),
                    "start": shift.shift_start.isoformat(),
                    "end": shift.shift_end.isoformat(),
                    "hours": shift_hours
                })
            
            employee_data = {
                "id": employee.id,
                "name": f"{employee.first_name} {employee.last_name}",
                "employee_number": employee.employee_number,
                "department": employee.department,
                "shifts": shift_list,
                "total_hours": round(total_hours, 2),
                "shift_count": len(shift_list)
            }
            
            # Add to appropriate position group
            position = employee.position
            if position in hierarchy_schedule:
                hierarchy_schedule[position]["employees"].append(employee_data)
                hierarchy_schedule[position]["total_hours"] += total_hours
                hierarchy_schedule[position]["employee_count"] += 1
            else:
                hierarchy_schedule["Other"]["employees"].append(employee_data)
                hierarchy_schedule["Other"]["total_hours"] += total_hours
                hierarchy_schedule["Other"]["employee_count"] += 1
        
        # Remove empty positions
        hierarchy_schedule = {
            k: v for k, v in hierarchy_schedule.items()
            if v["employee_count"] > 0
        }
        
        # Convert to list and sort by rank
        hierarchy_list = list(hierarchy_schedule.values())
        hierarchy_list.sort(key=lambda x: x["rank"])
        
        return {
            "department": department,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "hierarchy": hierarchy_list,
            "summary": {
                "total_positions": len(hierarchy_list),
                "total_employees": sum(p["employee_count"] for p in hierarchy_list),
                "total_hours": sum(p["total_hours"] for p in hierarchy_list)
            }
        }
    
    async def find_available_employees(
        self,
        target_date: date,
        target_time_start: time,
        target_time_end: time,
        department: str = None,
        position: str = None,
        exclude_employee_ids: List[int] = None
    ) -> List[Dict]:
        """
        Find employees available during a specific time window.
        
        Useful for finding coverage or scheduling new shifts.
        """
        # Get all active employees
        all_employees = await self.employee_repo.get_all_active()
        
        # Filter by criteria
        filtered_employees = []
        
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
            
            filtered_employees.append(employee)
        
        # Check availability
        available_employees = []
        
        for employee in filtered_employees:
            # Get shifts on target date
            shifts = await self.schedule_repo.get_by_employee_and_date(
                employee.id,
                target_date
            )
            
            # Check if any shift conflicts with target time
            is_available = True
            
            for shift in shifts:
                schedule_class = ScheduleClass(
                    employee_id=shift.employee_id,
                    shift_date=shift.shift_date,
                    shift_start=shift.shift_start,
                    shift_end=shift.shift_end
                )
                
                if schedule_class.overlaps_with(
                    target_time_start,
                    target_time_end,
                    target_date
                ):
                    is_available = False
                    break
            
            if is_available:
                # Check PTO/sick leave
                from Repositories.PaidTimeOffRepository import PaidTimeOffRepository
                pto_repo = PaidTimeOffRepository(self.session)
                
                pto_conflicts = await pto_repo.check_conflicts(
                    employee.id,
                    target_date,
                    target_date
                )
                
                if not pto_conflicts:
                    available_employees.append({
                        "employee_id": employee.id,
                        "name": f"{employee.first_name} {employee.last_name}",
                        "employee_number": employee.employee_number,
                        "position": employee.position,
                        "department": employee.department,
                        "location": employee.work_city
                    })
        
        return available_employees
