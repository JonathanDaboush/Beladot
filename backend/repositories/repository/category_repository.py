
# ------------------------------------------------------------------------------
# category_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing Category records from the database.
# Provides async methods for retrieving categories by ID.
# ------------------------------------------------------------------------------

from typing import Optional
from backend.persistance.category import Category
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class CategoryRepository:
    """
    Repository for Category model.
    Provides async methods to retrieve categories by ID.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with DB session."""
        self.db = db

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        """Retrieve a category by its ID."""
        result = await self.db.execute(
            select(Category).filter(Category.category_id == category_id)
        )
        return result.scalars().first()
