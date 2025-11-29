from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.EmployeeFinancial import EmployeeFinancial
from typing import Optional


class EmployeeFinancialRepository:
    """
    Repository for Employee Financial database operations.
    
    NOTE: This contains sensitive data. Access should be restricted to:
    - HR administrators
    - Payroll processors
    - The employee themselves (limited fields)
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, financial: EmployeeFinancial) -> EmployeeFinancial:
        """Create financial record for employee."""
        self.session.add(financial)
        await self.session.commit()
        await self.session.refresh(financial)
        return financial
    
    async def get_by_employee_id(self, employee_id: int) -> Optional[EmployeeFinancial]:
        """Get financial information for an employee."""
        result = await self.session.execute(
            select(EmployeeFinancial)
            .where(EmployeeFinancial.employee_id == employee_id)
        )
        return result.scalar_one_or_none()
    
    async def update(self, financial: EmployeeFinancial) -> EmployeeFinancial:
        """Update financial information."""
        from datetime import datetime
        financial.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(financial)
        return financial
    
    async def update_pay_rate(
        self, 
        employee_id: int, 
        new_pay_rate: float
    ) -> Optional[EmployeeFinancial]:
        """Update employee's pay rate."""
        financial = await self.get_by_employee_id(employee_id)
        if not financial:
            return None
        
        financial.pay_rate = new_pay_rate
        return await self.update(financial)
    
    async def update_bank_info(
        self,
        employee_id: int,
        bank_name: str,
        account_number: str,
        routing_number: str
    ) -> Optional[EmployeeFinancial]:
        """Update employee's banking information."""
        financial = await self.get_by_employee_id(employee_id)
        if not financial:
            return None
        
        financial.bank_name = bank_name
        financial.bank_account_number = account_number  # Should be encrypted
        financial.bank_routing_number = routing_number  # Should be encrypted
        
        return await self.update(financial)
    
    async def delete(self, employee_id: int) -> bool:
        """Delete financial record (use with caution - typically should archive instead)."""
        financial = await self.get_by_employee_id(employee_id)
        if not financial:
            return False
        
        await self.session.delete(financial)
        await self.session.commit()
        return True
