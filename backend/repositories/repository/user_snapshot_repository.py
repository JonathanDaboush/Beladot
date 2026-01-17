


"""
user_snapshot_repository.py

Repository class for managing UserSnapshot entities in the database.
Provides async method for retrieving user snapshots by full name.
"""

from backend.persistance.user_snapshot import UserSnapshot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class UserSnapshotRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, full_name):
        """
        Retrieve a user snapshot by full name.
        Args:
            full_name (str): The full name of the user.
        Returns:
            UserSnapshot or None
        """
        result = await self.db.execute(
            select(UserSnapshot).filter(UserSnapshot.full_name == full_name)
        )
        return result.scalars().first()
