
# ------------------------------------------------------------------------------
# product_rating_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing ProductRating records from the database.
# Provides async methods for retrieving product ratings by ID.
# ------------------------------------------------------------------------------

from backend.persistance.product_rating import ProductRating
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class ProductRatingRepository:
    """
    Repository for ProductRating model.
    Provides async methods to retrieve product ratings by ID.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_by_id(self, rating_id):
        """Retrieve a product rating by its ID."""
        result = await self.db.execute(
            select(ProductRating).filter(ProductRating.rating_id == rating_id)
        )
        return result.scalars().first()
