
# ------------------------------------------------------------------------------
# employee_component_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing EmployeeComponent records from the database.
# Provides async CRUD methods for employee components.
# ------------------------------------------------------------------------------

from backend.persistance.employee_component import EmployeeComponent
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class EmployeeComponentRepository:
    """
    Repository for EmployeeComponent model.
    Provides async CRUD operations for employee components.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_all(self):
        """Retrieve all employee components."""
        result = await self.db.execute(select(EmployeeComponent))
        return result.scalars().all()

    async def get_by_department(self, department_id):
        """Retrieve all employee components for a given department ID."""
        result = await self.db.execute(select(EmployeeComponent).filter(EmployeeComponent.department_id == department_id))
        return result.scalars().all()

    async def get_by_id(self, id):
        """Retrieve an employee component by its ID."""
        result = await self.db.execute(select(EmployeeComponent).filter(EmployeeComponent.id == id))
        return result.scalars().first()

    async def create(self, img_url, description, department_id):
        """Create a new employee component."""
        component = EmployeeComponent(img_url=img_url, description=description, department_id=department_id)
        self.db.add(component)
        await self.db.commit()
        await self.db.refresh(component)
        return component

    async def update(self, id, **kwargs):
        """Update an existing employee component by ID with provided fields."""
        component = await self.get_by_id(id)
        if not component:
            return None
        for k, v in kwargs.items():
            if hasattr(component, k):
                setattr(component, k, v)
        await self.db.commit()
        return component

    async def delete(self, id):
        """Delete an employee component by its ID."""
        component = await self.get_by_id(id)
        if not component:
            return False
        await self.db.delete(component)
        await self.db.commit()
        return True
