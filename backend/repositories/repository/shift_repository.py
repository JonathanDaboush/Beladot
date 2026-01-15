



"""
shift_repository.py

Repository class for managing Shift entities in the database.
Provides async methods for retrieving shifts by ID and by employee/time range.
"""

from backend.persistance.shift import Shift
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class ShiftRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def save(self, shift):
        """
        Save a new or updated shift to the database.
        Args:
            shift (Shift): The shift to save.
        Returns:
            Shift: The saved shift.
        """
        self.db.add(shift)
        await self.db.commit()
        await self.db.refresh(shift)
        return shift
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, shift_id):
        """
        Retrieve a shift by its ID.
        Args:
            shift_id (int): The ID of the shift.
        Returns:
            Shift or None
        """
        result = await self.db.execute(
            select(Shift).where(Shift.shift_id == shift_id)
        )
        return result.scalars().first()

    async def get_shifts_by_employee_and_time(self, employee_id, start_time, end_time):
        """
        Retrieve shifts for an employee within a time range.
        Args:
            employee_id (int): The employee's ID.
            start_time (datetime): Start of the time range.
            end_time (datetime): End of the time range.
        Returns:
            list[Shift]: List of shifts for the employee in the time range.
        """
        result = await self.db.execute(
            select(Shift).where(
                Shift.assigned_emp_id == employee_id,
                Shift.start_time >= start_time,
                Shift.end_time <= end_time
            )
        )
        return result.scalars().all()
