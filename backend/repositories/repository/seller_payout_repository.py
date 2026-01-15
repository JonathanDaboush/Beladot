


"""
seller_payout_repository.py

Repository class for managing SellerPayout entities in the database.
Provides async method for retrieving seller payouts by ID.
"""

from backend.model.seller_payout import SellerPayout
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class SellerPayoutRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, payout_id):
        """
        Retrieve a seller payout by its ID.
        Args:
            payout_id (int): The ID of the seller payout.
        Returns:
            SellerPayout or None
        """
        result = await self.db.execute(
            select(SellerPayout).filter(SellerPayout.payout_id == payout_id, SellerPayout.is_deleted == False)
        )
        return result.scalars().first()
