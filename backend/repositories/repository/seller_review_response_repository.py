


"""
seller_review_response_repository.py

Repository class for managing SellerReviewResponse entities in the database.
Provides async method for retrieving seller review responses by ID.
"""

from backend.persistance.seller_review_response import SellerReviewResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class SellerReviewResponseRepository:
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an async database session.
        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.db = db

    async def get_by_id(self, response_id):
        """
        Retrieve a seller review response by its ID.
        Args:
            response_id (int): The ID of the seller review response.
        Returns:
            SellerReviewResponse or None
        """
        result = await self.db.execute(
            select(SellerReviewResponse).filter(SellerReviewResponse.response_id == response_id)
        )
        return result.scalars().first()
