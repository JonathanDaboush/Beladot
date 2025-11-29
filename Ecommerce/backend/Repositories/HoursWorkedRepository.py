from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from Models.HoursWorked import HoursWorked
from Models.Employee import Employee
from typing import Optional, List
from datetime import date, datetime


class HoursWorkedRepository:
    """Repository for Hours Worked database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, hours: HoursWorked) -> HoursWorked:
        """Create hours worked entry."""
        self.session.add(hours)
        await self.session.commit()
        await self.session.refresh(hours)
        return hours
    
    async def get_by_id(self, hours_id: int) -> Optional[HoursWorked]:
        """Get hours entry by ID."""
        result = await self.session.execute(
            select(HoursWorked).where(HoursWorked.id == hours_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_employee_and_date(
        self, 
        employee_id: int, 
        work_date: date
    ) -> Optional[HoursWorked]:
        """Get hours entry for specific employee and date."""
        result = await self.session.execute(
            select(HoursWorked)
            .where(and_(
                HoursWorked.employee_id == employee_id,
                HoursWorked.work_date == work_date
            ))
        )
        return result.scalar_one_or_none()
    
    async def get_by_date_range(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> List[HoursWorked]:
        """Get all hours entries for employee within date range."""
        result = await self.session.execute(
            select(HoursWorked)
            .where(and_(
                HoursWorked.employee_id == employee_id,
                HoursWorked.work_date >= start_date,
                HoursWorked.work_date <= end_date
            ))
            .order_by(HoursWorked.work_date.desc())
        )
        return result.scalars().all()
    
    async def get_pending_approval(self, manager_id: int = None) -> List[HoursWorked]:
        """Get hours entries pending approval."""
        query = select(HoursWorked).where(HoursWorked.is_approved == False)
        
        if manager_id:
            # Filter by employees reporting to this manager
            query = query.join(HoursWorked.employee).where(Employee.manager_id == manager_id)
        
        result = await self.session.execute(query.order_by(HoursWorked.work_date.desc()))
        return result.scalars().all()
    
    async def get_unpaid_hours(self, employee_id: int) -> List[HoursWorked]:
        """Get approved but unpaid hours for an employee."""
        result = await self.session.execute(
            select(HoursWorked)
            .where(and_(
                HoursWorked.employee_id == employee_id,
                HoursWorked.is_approved == True,
                HoursWorked.is_paid == False
            ))
            .order_by(HoursWorked.work_date)
        )
        return result.scalars().all()
    
    async def calculate_total_hours(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> dict:
        """Calculate total hours by type for employee in date range."""
        result = await self.session.execute(
            select(
                func.sum(HoursWorked.regular_hours).label("total_regular"),
                func.sum(HoursWorked.overtime_hours).label("total_overtime"),
                func.sum(HoursWorked.double_time_hours).label("total_double_time"),
                func.sum(HoursWorked.holiday_hours).label("total_holiday"),
                func.sum(HoursWorked.total_hours).label("total_all")
            )
            .where(and_(
                HoursWorked.employee_id == employee_id,
                HoursWorked.work_date >= start_date,
                HoursWorked.work_date <= end_date,
                HoursWorked.is_approved == True
            ))
        )
        
        row = result.first()
        return {
            "regular_hours": float(row.total_regular or 0),
            "overtime_hours": float(row.total_overtime or 0),
            "double_time_hours": float(row.total_double_time or 0),
            "holiday_hours": float(row.total_holiday or 0),
            "total_hours": float(row.total_all or 0)
        }
    
    async def approve_hours(
        self,
        hours_id: int,
        approved_by: int
    ) -> Optional[HoursWorked]:
        """Approve hours worked entry."""
        hours = await self.get_by_id(hours_id)
        if not hours:
            return None
        
        hours.is_approved = True
        hours.approved_by = approved_by
        hours.approved_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(hours)
        return hours
    
    async def mark_as_paid(
        self,
        hours_ids: List[int],
        payroll_batch_id: int
    ) -> int:
        """Mark multiple hours entries as paid."""
        count = 0
        for hours_id in hours_ids:
            hours = await self.get_by_id(hours_id)
            if hours:
                hours.is_paid = True
                hours.payroll_batch_id = payroll_batch_id
                hours.paid_at = datetime.utcnow()
                count += 1
        
        await self.session.commit()
        return count
    
    async def update(self, hours: HoursWorked) -> HoursWorked:
        """Update hours worked entry."""
        hours.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(hours)
        return hours
    
    async def delete(self, hours_id: int) -> bool:
        """Delete hours entry (only if not approved or paid)."""
        hours = await self.get_by_id(hours_id)
        if not hours or hours.is_approved or hours.is_paid:
            return False
        
        await self.session.delete(hours)
        await self.session.commit()
        return True
