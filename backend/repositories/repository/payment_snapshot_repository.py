
# ------------------------------------------------------------------------------
# payment_snapshot_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing PaymentSnapshot records from the database.
# Provides async methods for retrieving payment snapshots by order number.
# ------------------------------------------------------------------------------

from backend.model.payment_snapshot import PaymentSnapshot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class PaymentSnapshotRepository:
    """
    Repository for PaymentSnapshot model.
    Provides async methods to retrieve payment snapshots by order number.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_by_id(self, order_number):
        """Retrieve a payment snapshot by order number."""
        result = await self.db.execute(
            select(PaymentSnapshot).filter(PaymentSnapshot.order_number == order_number)
        )
        return result.scalars().first()
