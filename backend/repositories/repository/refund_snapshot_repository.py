


"""
refund_snapshot_repository.py

Repository class for managing RefundSnapshot entities in the database.
Provides async method for retrieving refund snapshots by order number.
"""

from backend.persistance.refund_snapshot import RefundSnapshot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class RefundSnapshotRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, order_number):
        """
        Retrieve a RefundSnapshot by order number.
        Args:
            order_number (int): The order number for the refund snapshot.
        Returns:
            RefundSnapshot or None
        """
        result = await self.db.execute(
            select(RefundSnapshot).filter(RefundSnapshot.order_number == order_number)
        )
        return result.scalars().first()
