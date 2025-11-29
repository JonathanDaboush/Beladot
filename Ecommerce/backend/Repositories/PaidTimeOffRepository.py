from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from Models.PaidTimeOff import PaidTimeOff, PTOStatus
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class PaidTimeOffRepository:
    """Repository for Paid Time Off database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, pto: PaidTimeOff) -> PaidTimeOff:
        """Create PTO request."""
        self.session.add(pto)
        await self.session.commit()
        await self.session.refresh(pto)
        return pto
    
    async def get_by_id(self, pto_id: int) -> Optional[PaidTimeOff]:
        """Get PTO request by ID."""
        result = await self.session.execute(
            select(PaidTimeOff).where(PaidTimeOff.id == pto_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_employee(
        self,
        employee_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[PaidTimeOff]:
        """Get all PTO requests for an employee."""
        result = await self.session.execute(
            select(PaidTimeOff)
            .where(PaidTimeOff.employee_id == employee_id)
            .order_by(PaidTimeOff.start_date.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_pending_requests(self, manager_id: int = None) -> List[PaidTimeOff]:
        """Get pending PTO requests."""
        query = select(PaidTimeOff).where(PaidTimeOff.status == PTOStatus.PENDING)
        
        if manager_id:
            from Models.Employee import Employee
            query = query.join(PaidTimeOff.employee).where(Employee.manager_id == manager_id)
        
        result = await self.session.execute(query.order_by(PaidTimeOff.requested_at))
        return result.scalars().all()
    
    async def get_approved_by_date_range(
        self,
        start_date: date,
        end_date: date,
        employee_id: int = None
    ) -> List[PaidTimeOff]:
        """Get approved PTO within a date range."""
        query = select(PaidTimeOff).where(and_(
            PaidTimeOff.status == PTOStatus.APPROVED,
            PaidTimeOff.start_date <= end_date,
            PaidTimeOff.end_date >= start_date
        ))
        
        if employee_id:
            query = query.where(PaidTimeOff.employee_id == employee_id)
        
        result = await self.session.execute(query.order_by(PaidTimeOff.start_date))
        return result.scalars().all()
    
    async def calculate_pto_balance(
        self,
        employee_id: int,
        accrual_rate: Decimal,
        year: int = None
    ) -> dict:
        """
        Calculate PTO balance for employee.
        
        Returns dict with accrued, used, and remaining hours.
        """
        if year is None:
            year = date.today().year
        
        start_of_year = date(year, 1, 1)
        end_of_year = date(year, 12, 31)
        
        # Get approved PTO used this year
        result = await self.session.execute(
            select(func.sum(PaidTimeOff.hours_requested))
            .where(and_(
                PaidTimeOff.employee_id == employee_id,
                PaidTimeOff.status == PTOStatus.APPROVED,
                PaidTimeOff.start_date >= start_of_year,
                PaidTimeOff.start_date <= end_of_year
            ))
        )
        
        hours_used = result.scalar() or Decimal("0")
        
        # Calculate accrued based on pay periods elapsed
        from datetime import timedelta
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
    
    async def approve_request(
        self,
        pto_id: int,
        reviewed_by: int
    ) -> Optional[PaidTimeOff]:
        """Approve PTO request."""
        pto = await self.get_by_id(pto_id)
        if not pto:
            return None
        
        pto.status = PTOStatus.APPROVED
        pto.reviewed_by = reviewed_by
        pto.reviewed_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(pto)
        return pto
    
    async def deny_request(
        self,
        pto_id: int,
        reviewed_by: int,
        denial_reason: str
    ) -> Optional[PaidTimeOff]:
        """Deny PTO request."""
        pto = await self.get_by_id(pto_id)
        if not pto:
            return None
        
        pto.status = PTOStatus.DENIED
        pto.reviewed_by = reviewed_by
        pto.reviewed_at = datetime.utcnow()
        pto.denial_reason = denial_reason
        
        await self.session.commit()
        await self.session.refresh(pto)
        return pto
    
    async def cancel_request(self, pto_id: int) -> Optional[PaidTimeOff]:
        """Cancel PTO request (by employee before approval)."""
        pto = await self.get_by_id(pto_id)
        if not pto or pto.status != PTOStatus.PENDING:
            return None
        
        pto.status = PTOStatus.CANCELLED
        await self.session.commit()
        await self.session.refresh(pto)
        return pto
    
    async def check_conflicts(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        exclude_pto_id: int = None
    ) -> List[PaidTimeOff]:
        """Check for conflicting PTO requests."""
        query = select(PaidTimeOff).where(and_(
            PaidTimeOff.employee_id == employee_id,
            PaidTimeOff.status == PTOStatus.APPROVED,
            PaidTimeOff.start_date <= end_date,
            PaidTimeOff.end_date >= start_date
        ))
        
        if exclude_pto_id:
            query = query.where(PaidTimeOff.id != exclude_pto_id)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update(self, pto: PaidTimeOff) -> PaidTimeOff:
        """Update PTO request."""
        pto.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(pto)
        return pto
