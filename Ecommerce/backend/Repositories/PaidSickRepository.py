from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from Models.PaidSick import PaidSick, SickLeaveStatus
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class PaidSickRepository:
    """Repository for Paid Sick Leave database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, sick: PaidSick) -> PaidSick:
        """Create sick leave request."""
        self.session.add(sick)
        await self.session.commit()
        await self.session.refresh(sick)
        return sick
    
    async def get_by_id(self, sick_id: int) -> Optional[PaidSick]:
        """Get sick leave request by ID."""
        result = await self.session.execute(
            select(PaidSick).where(PaidSick.id == sick_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_employee(
        self,
        employee_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[PaidSick]:
        """Get all sick leave requests for an employee."""
        result = await self.session.execute(
            select(PaidSick)
            .where(PaidSick.employee_id == employee_id)
            .order_by(PaidSick.start_date.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_pending_requests(self, manager_id: int = None) -> List[PaidSick]:
        """Get pending sick leave requests."""
        query = select(PaidSick).where(PaidSick.status == SickLeaveStatus.PENDING)
        
        if manager_id:
            from Models.Employee import Employee
            query = query.join(PaidSick.employee).where(Employee.manager_id == manager_id)
        
        result = await self.session.execute(query.order_by(PaidSick.reported_at))
        return result.scalars().all()
    
    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        employee_id: int = None
    ) -> List[PaidSick]:
        """Get approved sick leave within a date range."""
        query = select(PaidSick).where(and_(
            PaidSick.status == SickLeaveStatus.APPROVED,
            PaidSick.start_date <= end_date,
            PaidSick.end_date >= start_date
        ))
        
        if employee_id:
            query = query.where(PaidSick.employee_id == employee_id)
        
        result = await self.session.execute(query.order_by(PaidSick.start_date))
        return result.scalars().all()
    
    async def calculate_sick_balance(
        self,
        employee_id: int,
        accrual_rate: Decimal,
        year: int = None
    ) -> dict:
        """Calculate sick leave balance for employee."""
        if year is None:
            year = date.today().year
        
        start_of_year = date(year, 1, 1)
        end_of_year = date(year, 12, 31)
        
        # Get approved sick leave used this year
        result = await self.session.execute(
            select(func.sum(PaidSick.hours_requested))
            .where(and_(
                PaidSick.employee_id == employee_id,
                PaidSick.status == SickLeaveStatus.APPROVED,
                PaidSick.start_date >= start_of_year,
                PaidSick.start_date <= end_of_year
            ))
        )
        
        hours_used = result.scalar() or Decimal("0")
        
        # Calculate accrued based on pay periods elapsed
        days_elapsed = (date.today() - start_of_year).days
        pay_periods_elapsed = days_elapsed / 14  # Bi-weekly
        hours_accrued = accrual_rate * Decimal(str(pay_periods_elapsed))
        
        hours_remaining = hours_accrued - hours_used
        
        return {
            "hours_accrued": float(hours_accrued),
            "hours_used": float(hours_used),
            "hours_remaining": float(hours_remaining),
            "year": year
        }
    
    async def get_requiring_doctors_note(self) -> List[PaidSick]:
        """Get sick leave requests requiring doctor's note."""
        result = await self.session.execute(
            select(PaidSick)
            .where(and_(
                PaidSick.requires_doctors_note == True,
                PaidSick.doctors_note_provided == False,
                PaidSick.status == SickLeaveStatus.APPROVED
            ))
        )
        return result.scalars().all()
    
    async def get_workers_comp_cases(self) -> List[PaidSick]:
        """Get all workers' compensation related sick leave."""
        result = await self.session.execute(
            select(PaidSick)
            .where(PaidSick.is_reportable == True)
            .order_by(PaidSick.start_date.desc())
        )
        return result.scalars().all()
    
    async def approve_request(
        self,
        sick_id: int,
        reviewed_by: int
    ) -> Optional[PaidSick]:
        """Approve sick leave request."""
        sick = await self.get_by_id(sick_id)
        if not sick:
            return None
        
        sick.status = SickLeaveStatus.APPROVED
        sick.reviewed_by = reviewed_by
        sick.reviewed_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(sick)
        return sick
    
    async def deny_request(
        self,
        sick_id: int,
        reviewed_by: int,
        denial_reason: str
    ) -> Optional[PaidSick]:
        """Deny sick leave request."""
        sick = await self.get_by_id(sick_id)
        if not sick:
            return None
        
        sick.status = SickLeaveStatus.DENIED
        sick.reviewed_by = reviewed_by
        sick.reviewed_at = datetime.utcnow()
        sick.denial_reason = denial_reason
        
        await self.session.commit()
        await self.session.refresh(sick)
        return sick
    
    async def mark_doctors_note_received(
        self,
        sick_id: int,
        doctors_note_url: str
    ) -> Optional[PaidSick]:
        """Mark that doctor's note has been received."""
        sick = await self.get_by_id(sick_id)
        if not sick:
            return None
        
        sick.doctors_note_provided = True
        sick.doctors_note_url = doctors_note_url
        
        await self.session.commit()
        await self.session.refresh(sick)
        return sick
    
    async def update(self, sick: PaidSick) -> PaidSick:
        """Update sick leave request."""
        sick.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(sick)
        return sick
