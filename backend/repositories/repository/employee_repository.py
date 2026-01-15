
# ------------------------------------------------------------------------------
# employee_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing Employee records from the database.
# Provides methods for retrieving employees by ID and department.
# ------------------------------------------------------------------------------

from backend.persistance.employee import Employee
from sqlalchemy import select, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

class EmployeeRepository:
    """
    Repository for Employee model.
    Provides methods to retrieve employees by ID and department.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def update(self, emp_id, **kwargs):
        """Async update an employee's fields by their ID."""
        await self.db.execute(
            sql_update(Employee)
            .where(Employee.emp_id == emp_id)
            .values(**kwargs)
        )
        await self.db.commit()
        result = await self.db.execute(select(Employee).where(Employee.emp_id == emp_id))
        return result.scalar_one_or_none()
    def __init__(self, db):
        """Initialize repository with DB session."""
        self.db = db

    async def get_by_id(self, emp_id):
        """Async retrieve an employee by their ID."""
        result = await self.db.execute(select(Employee).where(Employee.emp_id == emp_id))
        return result.scalar_one_or_none()

    async def get_all_employees(self, department_id=None):
        """Async retrieve all employees, optionally filtered by department ID."""
        stmt = select(Employee)
        if department_id is not None:
            stmt = stmt.where(Employee.department_id == department_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
