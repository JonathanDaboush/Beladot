"""
refund_repository.py

Repository class for managing Refund entities in the database.
Provides async methods for retrieving refunds by ID.
"""

from backend.model.refund import Refund
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class RefundRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, refund_id):
        """
        Retrieve a refund by its ID.
        Args:
            refund_id (int): The ID of the refund.
        Returns:
            Refund or None
        """
        result = await self.db.execute(
            select(Refund).filter(Refund.refund_id == refund_id)
        )
        return result.scalars().first()
