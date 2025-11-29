"""
Simple Schedule Comparison Service

Streamlined comparison showing who works with a target employee based on position and location.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from Repositories.EmployeeRepository import EmployeeRepository
from Repositories.EmployeeScheduleRepository import EmployeeScheduleRepository
from typing import List, Dict
from datetime import datetime, date, time
import logging

logger = logging.getLogger(__name__)


class SimpleScheduleComparison:
    """Simplified service for comparing employee schedules."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.employee_repo = EmployeeRepository(session)
        self.schedule_repo = EmployeeScheduleRepository(session)
    
    async def compare_with_target(
        self,
        target_employee_id: int,
        start_datetime: datetime,
        end_datetime: datetime
    ) -> Dict:
        """
        Compare schedules with target employee based on their position and location.
        
        Shows all employees in same position/location who work during the time frame.
        
        Args:
            target_employee_id: The employee to compare against
            start_datetime: Start of time frame (datetime with date and time)
            end_datetime: End of time frame (datetime with date and time)
        
        Returns:
            Dict with target employee info and list of coworkers with their shifts
        """
        # Get target employee
        target_employee = await self.employee_repo.get_by_id(target_employee_id)
        if not target_employee:
            raise ValueError(f"Target employee {target_employee_id} not found")
        
        # Extract date range
        start_date = start_datetime.date()
        end_date = end_datetime.date()
        start_time = start_datetime.time()
        end_time = end_datetime.time()
        
        # Find employees with same position and location
        all_employees = await self.employee_repo.get_all_active()
        
        matching_employees = []
        for employee in all_employees:
            if employee.id == target_employee_id:
                continue
            
            # Match position and location
            if (employee.position == target_employee.position and 
                employee.work_city == target_employee.work_city):
                matching_employees.append(employee)
        
        # Get shifts for each matching employee in the time frame
        results = []
        
        for employee in matching_employees:
            shifts = await self.schedule_repo.get_by_date_range(
                employee.id,
                start_date,
                end_date
            )
            
            # Filter shifts that fall within the time window
            matching_shifts = []
            
            for shift in shifts:
                shift_start_dt = datetime.combine(shift.shift_date, shift.shift_start)
                shift_end_dt = datetime.combine(shift.shift_date, shift.shift_end)
                
                # Handle overnight shifts
                if shift_end_dt <= shift_start_dt:
                    from datetime import timedelta
                    shift_end_dt += timedelta(days=1)
                
                # Check if shift overlaps with requested time frame
                if shift_start_dt < end_datetime and shift_end_dt > start_datetime:
                    matching_shifts.append({
                        "employee_id": employee.id,
                        "start_datetime": shift_start_dt.isoformat(),
                        "end_datetime": shift_end_dt.isoformat()
                    })
            
            if matching_shifts:
                results.append({
                    "employee_id": employee.id,
                    "employee_name": f"{employee.first_name} {employee.last_name}",
                    "employee_number": employee.employee_number,
                    "shifts": matching_shifts
                })
        
        return {
            "target_employee": {
                "id": target_employee.id,
                "name": f"{target_employee.first_name} {target_employee.last_name}",
                "position": target_employee.position,
                "location": target_employee.work_city
            },
            "time_frame": {
                "start": start_datetime.isoformat(),
                "end": end_datetime.isoformat()
            },
            "coworkers": results,
            "total_coworkers": len(results)
        }
    
    async def find_all_by_position_and_location(
        self,
        position: str,
        location: str,
        start_datetime: datetime,
        end_datetime: datetime
    ) -> Dict:
        """
        Find all employees with specific position and location who work during time frame.
        
        No target employee - just finds everyone matching criteria.
        
        Args:
            position: Job position/title to filter by
            location: Work location/city to filter by
            start_datetime: Start of time frame (datetime with date and time)
            end_datetime: End of time frame (datetime with date and time)
        
        Returns:
            Dict with list of all employees and their shifts
        """
        # Extract date range
        start_date = start_datetime.date()
        end_date = end_datetime.date()
        
        # Find employees with matching position and location
        all_employees = await self.employee_repo.get_all_active()
        
        matching_employees = []
        for employee in all_employees:
            if employee.position == position and employee.work_city == location:
                matching_employees.append(employee)
        
        if not matching_employees:
            return {
                "position": position,
                "location": location,
                "time_frame": {
                    "start": start_datetime.isoformat(),
                    "end": end_datetime.isoformat()
                },
                "employees": [],
                "total_employees": 0,
                "message": f"No employees found with position '{position}' in '{location}'"
            }
        
        # Get shifts for each matching employee in the time frame
        results = []
        
        for employee in matching_employees:
            shifts = await self.schedule_repo.get_by_date_range(
                employee.id,
                start_date,
                end_date
            )
            
            # Filter shifts that fall within the time window
            matching_shifts = []
            
            for shift in shifts:
                shift_start_dt = datetime.combine(shift.shift_date, shift.shift_start)
                shift_end_dt = datetime.combine(shift.shift_date, shift.shift_end)
                
                # Handle overnight shifts
                if shift_end_dt <= shift_start_dt:
                    from datetime import timedelta
                    shift_end_dt += timedelta(days=1)
                
                # Check if shift overlaps with requested time frame
                if shift_start_dt < end_datetime and shift_end_dt > start_datetime:
                    matching_shifts.append({
                        "employee_id": employee.id,
                        "start_datetime": shift_start_dt.isoformat(),
                        "end_datetime": shift_end_dt.isoformat()
                    })
            
            # Include employee even if they have no shifts in this period
            results.append({
                "employee_id": employee.id,
                "employee_name": f"{employee.first_name} {employee.last_name}",
                "employee_number": employee.employee_number,
                "shifts": matching_shifts,
                "shift_count": len(matching_shifts)
            })
        
        return {
            "position": position,
            "location": location,
            "time_frame": {
                "start": start_datetime.isoformat(),
                "end": end_datetime.isoformat()
            },
            "employees": results,
            "total_employees": len(results),
            "employees_with_shifts": sum(1 for e in results if e["shift_count"] > 0),
            "total_shifts": sum(e["shift_count"] for e in results)
        }
