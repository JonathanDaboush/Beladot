"""
Employee Schedule Repository

Data access layer for shift scheduling and calendar management.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, Date, cast
from Models.EmployeeSchedule import EmployeeSchedule, ScheduleStatus
from typing import Optional, List, Dict
from datetime import date, time, datetime, timedelta


class EmployeeScheduleRepository:
    """Repository for employee schedule operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, schedule: EmployeeSchedule) -> EmployeeSchedule:
        """Create a new schedule entry."""
        schedule.created_at = datetime.now()
        schedule.updated_at = datetime.now()
        
        self.session.add(schedule)
        await self.session.commit()
        await self.session.refresh(schedule)
        
        return schedule
    
    async def get_by_id(self, schedule_id: int) -> Optional[EmployeeSchedule]:
        """Get schedule by ID."""
        result = await self.session.execute(
            select(EmployeeSchedule).where(EmployeeSchedule.id == schedule_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_employee_and_date(
        self,
        employee_id: int,
        shift_date: date
    ) -> List[EmployeeSchedule]:
        """Get all shifts for an employee on a specific date."""
        result = await self.session.execute(
            select(EmployeeSchedule).where(
                and_(
                    EmployeeSchedule.employee_id == employee_id,
                    EmployeeSchedule.shift_date == shift_date,
                    EmployeeSchedule.status != ScheduleStatus.CANCELLED
                )
            ).order_by(EmployeeSchedule.shift_start)
        )
        return result.scalars().all()
    
    async def get_by_date_range(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> List[EmployeeSchedule]:
        """Get all shifts for an employee in a date range."""
        result = await self.session.execute(
            select(EmployeeSchedule).where(
                and_(
                    EmployeeSchedule.employee_id == employee_id,
                    EmployeeSchedule.shift_date >= start_date,
                    EmployeeSchedule.shift_date <= end_date,
                    EmployeeSchedule.status != ScheduleStatus.CANCELLED
                )
            ).order_by(EmployeeSchedule.shift_date, EmployeeSchedule.shift_start)
        )
        return result.scalars().all()
    
    async def get_weekly_schedule(
        self,
        employee_id: int,
        week_start: date
    ) -> List[EmployeeSchedule]:
        """Get employee's schedule for a week."""
        week_end = week_start + timedelta(days=6)
        return await self.get_by_date_range(employee_id, week_start, week_end)
    
    async def get_department_schedule(
        self,
        department: str,
        shift_date: date
    ) -> List[EmployeeSchedule]:
        """Get all shifts for a department on a specific date."""
        result = await self.session.execute(
            select(EmployeeSchedule).where(
                and_(
                    EmployeeSchedule.department == department,
                    EmployeeSchedule.shift_date == shift_date,
                    EmployeeSchedule.status != ScheduleStatus.CANCELLED
                )
            ).order_by(EmployeeSchedule.shift_start)
        )
        return result.scalars().all()
    
    async def get_location_schedule(
        self,
        location: str,
        start_date: date,
        end_date: date
    ) -> List[EmployeeSchedule]:
        """Get all shifts for a location in a date range."""
        result = await self.session.execute(
            select(EmployeeSchedule).where(
                and_(
                    EmployeeSchedule.location == location,
                    EmployeeSchedule.shift_date >= start_date,
                    EmployeeSchedule.shift_date <= end_date,
                    EmployeeSchedule.status != ScheduleStatus.CANCELLED
                )
            ).order_by(EmployeeSchedule.shift_date, EmployeeSchedule.shift_start)
        )
        return result.scalars().all()
    
    async def get_unconfirmed_shifts(
        self,
        start_date: date,
        end_date: date
    ) -> List[EmployeeSchedule]:
        """Get shifts that haven't been confirmed by employees."""
        result = await self.session.execute(
            select(EmployeeSchedule).where(
                and_(
                    EmployeeSchedule.shift_date >= start_date,
                    EmployeeSchedule.shift_date <= end_date,
                    EmployeeSchedule.is_confirmed == False,
                    EmployeeSchedule.status == ScheduleStatus.SCHEDULED
                )
            ).order_by(EmployeeSchedule.shift_date)
        )
        return result.scalars().all()
    
    async def get_coverage_needed(
        self,
        start_date: date,
        end_date: date,
        location: str = None
    ) -> List[EmployeeSchedule]:
        """Get shifts that need coverage."""
        query = select(EmployeeSchedule).where(
            and_(
                EmployeeSchedule.shift_date >= start_date,
                EmployeeSchedule.shift_date <= end_date,
                EmployeeSchedule.is_coverage_needed == True,
                EmployeeSchedule.covered_by == None
            )
        )
        
        if location:
            query = query.where(EmployeeSchedule.location == location)
        
        result = await self.session.execute(
            query.order_by(EmployeeSchedule.shift_date, EmployeeSchedule.shift_start)
        )
        return result.scalars().all()
    
    async def check_overlap(
        self,
        employee_id: int,
        shift_date: date,
        shift_start: time,
        shift_end: time,
        exclude_schedule_id: int = None
    ) -> bool:
        """
        Check if a shift overlaps with existing schedules.
        
        Returns True if overlap exists.
        """
        query = select(EmployeeSchedule).where(
            and_(
                EmployeeSchedule.employee_id == employee_id,
                EmployeeSchedule.shift_date == shift_date,
                EmployeeSchedule.status != ScheduleStatus.CANCELLED
            )
        )
        
        if exclude_schedule_id:
            query = query.where(EmployeeSchedule.id != exclude_schedule_id)
        
        result = await self.session.execute(query)
        existing_shifts = result.scalars().all()
        
        # Check for time overlap
        for existing in existing_shifts:
            # Simple overlap check (doesn't handle overnight shifts perfectly)
            if (shift_start < existing.shift_end and shift_end > existing.shift_start):
                return True
        
        return False
    
    async def confirm_shift(self, schedule_id: int) -> Optional[EmployeeSchedule]:
        """Employee confirms their scheduled shift."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return None
        
        schedule.is_confirmed = True
        schedule.confirmed_at = datetime.now()
        schedule.status = ScheduleStatus.CONFIRMED
        schedule.updated_at = datetime.now()
        
        await self.session.commit()
        await self.session.refresh(schedule)
        
        return schedule
    
    async def mark_no_show(self, schedule_id: int) -> Optional[EmployeeSchedule]:
        """Mark employee as no-show for shift."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return None
        
        schedule.status = ScheduleStatus.NO_SHOW
        schedule.is_coverage_needed = True
        schedule.updated_at = datetime.now()
        
        await self.session.commit()
        await self.session.refresh(schedule)
        
        return schedule
    
    async def assign_coverage(
        self,
        schedule_id: int,
        covered_by: int,
        notes: str = None
    ) -> Optional[EmployeeSchedule]:
        """Assign coverage for a shift."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return None
        
        schedule.covered_by = covered_by
        schedule.is_coverage_needed = False
        schedule.coverage_notes = notes
        schedule.updated_at = datetime.now()
        
        await self.session.commit()
        await self.session.refresh(schedule)
        
        return schedule
    
    async def cancel_shift(
        self,
        schedule_id: int,
        reason: str = None
    ) -> Optional[EmployeeSchedule]:
        """Cancel a scheduled shift."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return None
        
        schedule.status = ScheduleStatus.CANCELLED
        schedule.manager_notes = reason
        schedule.updated_at = datetime.now()
        
        await self.session.commit()
        await self.session.refresh(schedule)
        
        return schedule
    
    async def complete_shift(self, schedule_id: int) -> Optional[EmployeeSchedule]:
        """Mark shift as completed."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return None
        
        schedule.status = ScheduleStatus.COMPLETED
        schedule.updated_at = datetime.now()
        
        await self.session.commit()
        await self.session.refresh(schedule)
        
        return schedule
    
    async def calculate_weekly_hours(
        self,
        employee_id: int,
        week_start: date
    ) -> Dict:
        """Calculate total scheduled hours for a week."""
        week_end = week_start + timedelta(days=6)
        shifts = await self.get_by_date_range(employee_id, week_start, week_end)
        
        total_hours = 0.0
        shift_count = len(shifts)
        
        for shift in shifts:
            # Calculate shift duration
            from Classes.EmployeeSchedule import EmployeeSchedule as ScheduleClass
            schedule_class = ScheduleClass(
                employee_id=shift.employee_id,
                shift_date=shift.shift_date,
                shift_start=shift.shift_start,
                shift_end=shift.shift_end,
                unpaid_break_minutes=shift.unpaid_break_minutes,
                paid_break_minutes=shift.paid_break_minutes
            )
            total_hours += schedule_class.calculate_paid_hours()
        
        return {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "total_hours": round(total_hours, 2),
            "shift_count": shift_count,
            "average_per_day": round(total_hours / 7, 2) if total_hours > 0 else 0
        }
    
    async def get_staffing_summary(
        self,
        shift_date: date,
        location: str = None,
        department: str = None
    ) -> Dict:
        """Get staffing summary for a specific date."""
        query = select(EmployeeSchedule).where(
            and_(
                EmployeeSchedule.shift_date == shift_date,
                EmployeeSchedule.status.in_([
                    ScheduleStatus.SCHEDULED,
                    ScheduleStatus.CONFIRMED,
                    ScheduleStatus.COMPLETED
                ])
            )
        )
        
        if location:
            query = query.where(EmployeeSchedule.location == location)
        if department:
            query = query.where(EmployeeSchedule.department == department)
        
        result = await self.session.execute(query)
        shifts = result.scalars().all()
        
        confirmed_count = sum(1 for s in shifts if s.is_confirmed)
        coverage_needed = sum(1 for s in shifts if s.is_coverage_needed)
        
        return {
            "date": shift_date.isoformat(),
            "location": location,
            "department": department,
            "total_shifts": len(shifts),
            "confirmed_shifts": confirmed_count,
            "unconfirmed_shifts": len(shifts) - confirmed_count,
            "coverage_needed": coverage_needed
        }
    
    async def update(self, schedule: EmployeeSchedule) -> EmployeeSchedule:
        """Update schedule entry."""
        schedule.updated_at = datetime.now()
        await self.session.commit()
        await self.session.refresh(schedule)
        return schedule
    
    async def delete(self, schedule_id: int) -> bool:
        """Delete schedule entry."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return False
        
        await self.session.delete(schedule)
        await self.session.commit()
        return True
