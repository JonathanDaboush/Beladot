
# ------------------------------------------------------------------------------
# payment_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing Payment records from the database.
# Provides async methods for retrieving payments by ID.
# ------------------------------------------------------------------------------

from backend.persistance.payment import Payment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class PaymentRepository:
    """
    Repository for Payment model.
    Provides async methods to retrieve payments by ID.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_by_id(self, payment_id):
        """Retrieve a payment by its ID."""
        result = await self.db.execute(
            select(Payment).filter(Payment.payment_id == payment_id)
        )
        return result.scalars().first()
