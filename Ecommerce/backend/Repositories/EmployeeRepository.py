from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from Models.Employee import Employee, EmploymentStatus
from typing import Optional, List
from datetime import date, datetime


class EmployeeRepository:
    """Repository for Employee database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, employee: Employee) -> Employee:
        """Create a new employee."""
        self.session.add(employee)
        await self.session.commit()
        await self.session.refresh(employee)
        return employee
    
    async def get_by_id(self, employee_id: int) -> Optional[Employee]:
        """Get employee by ID."""
        result = await self.session.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_employee_number(self, employee_number: str) -> Optional[Employee]:
        """Get employee by employee number."""
        result = await self.session.execute(
            select(Employee).where(Employee.employee_number == employee_number)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email."""
        result = await self.session.execute(
            select(Employee).where(Employee.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_all_active(self, limit: int = 100, offset: int = 0) -> List[Employee]:
        """Get all active employees."""
        result = await self.session.execute(
            select(Employee)
            .where(and_(
                Employee.is_active == True,
                Employee.employment_status == EmploymentStatus.ACTIVE
            ))
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_by_department(self, department: str) -> List[Employee]:
        """Get all employees in a department."""
        result = await self.session.execute(
            select(Employee)
            .where(and_(
                Employee.department == department,
                Employee.is_active == True
            ))
        )
        return result.scalars().all()
    
    async def get_by_manager(self, manager_id: int) -> List[Employee]:
        """Get all employees reporting to a manager."""
        result = await self.session.execute(
            select(Employee)
            .where(and_(
                Employee.manager_id == manager_id,
                Employee.is_active == True
            ))
        )
        return result.scalars().all()
    
    async def get_by_hire_date_range(self, start_date: date, end_date: date) -> List[Employee]:
        """Get employees hired within a date range."""
        result = await self.session.execute(
            select(Employee)
            .where(and_(
                Employee.hire_date >= start_date,
                Employee.hire_date <= end_date
            ))
        )
        return result.scalars().all()
    
    async def search_employees(self, search_term: str) -> List[Employee]:
        """Search employees by name, email, or employee number."""
        search_pattern = f"%{search_term}%"
        result = await self.session.execute(
            select(Employee)
            .where(or_(
                Employee.first_name.ilike(search_pattern),
                Employee.last_name.ilike(search_pattern),
                Employee.email.ilike(search_pattern),
                Employee.employee_number.ilike(search_pattern)
            ))
            .where(Employee.is_active == True)
        )
        return result.scalars().all()
    
    async def update(self, employee: Employee) -> Employee:
        """Update employee information."""
        employee.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(employee)
        return employee
    
    async def terminate_employee(
        self, 
        employee_id: int, 
        termination_date: date
    ) -> Optional[Employee]:
        """Terminate an employee."""
        employee = await self.get_by_id(employee_id)
        if not employee:
            return None
        
        employee.employment_status = EmploymentStatus.TERMINATED
        employee.termination_date = termination_date
        employee.is_active = False
        employee.updated_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(employee)
        return employee
    
    async def count_active_employees(self) -> int:
        """Count total active employees."""
        result = await self.session.execute(
            select(func.count(Employee.id))
            .where(and_(
                Employee.is_active == True,
                Employee.employment_status == EmploymentStatus.ACTIVE
            ))
        )
        return result.scalar()
    
    async def get_employees_needing_review(self, months: int = 12) -> List[Employee]:
        """
        Get employees due for annual review.
        Returns employees hired X months ago.
        """
        from datetime import timedelta
        review_date = date.today() - timedelta(days=months * 30)
        
        result = await self.session.execute(
            select(Employee)
            .where(and_(
                Employee.hire_date <= review_date,
                Employee.is_active == True
            ))
        )
        return result.scalars().all()
