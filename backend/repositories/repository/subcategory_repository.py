


"""
subcategory_repository.py

Repository class for managing Subcategory entities in the database.
Provides async method for retrieving subcategories by ID.
"""

from backend.model.subcategory import Subcategory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class SubcategoryRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, subcategory_id):
        """
        Retrieve a subcategory by its ID.
        Args:
            subcategory_id (int): The ID of the subcategory.
        Returns:
            Subcategory or None
        """
        result = await self.db.execute(
            select(Subcategory).filter(Subcategory.subcategory_id == subcategory_id)
        )
        return result.scalars().first()
