
# ------------------------------------------------------------------------------
# manager_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing Manager records from the database.
# Provides methods for retrieving managers by ID.
# ------------------------------------------------------------------------------

from backend.persistance.manager import Manager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class ManagerRepository:
    """
    Repository for Manager model.
    Provides methods to retrieve managers by ID.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_by_id(self, manager_id):
        """Async retrieve a manager by their ID."""
        result = await self.db.execute(select(Manager).where(Manager.manager_id == manager_id))
        return result.scalar_one_or_none()
